"""D3 explicit offline-first research pipeline.

Sources are acquired only from caller-approved URLs/hosts. Agent claims and
peer assessments are advisory, never automatic verification.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Callable
from .acquisition import fetch_source, Acquisition
from .research_index import index_acquisition, candidate_passages
from .claim_review import parse_claim_drafts, cross_agent_review_packet
from .core import JobStore, Mission, lemonade_chat
from .specialists import system_prompt, SPECIALISTS
from .vetting import vet_claim, VettingPolicy, AuditLog

@dataclass(frozen=True)
class PipelineRequest:
    suite: str
    question: str
    approved_scope: str
    source_urls: tuple[str, ...] = ()
    approved_hosts: frozenset[str] = frozenset()
    reviewer_suite: str | None = None
    vetting_enabled: bool = False

    def validate(self):
        if self.suite not in SPECIALISTS or not self.question.strip():
            raise ValueError("Unknown specialist or empty question")
        if len(self.source_urls) > 8 or len(set(self.source_urls)) != len(self.source_urls):
            raise ValueError("Maximum eight distinct approved source URLs")
        if self.source_urls and not self.approved_hosts:
            raise ValueError("Explicitly approved hosts required")
        if self.vetting_enabled and self.reviewer_suite is None:
            raise ValueError('Vetting requires a distinct reviewer suite')
        if self.reviewer_suite is not None and (
            self.reviewer_suite not in SPECIALISTS or self.reviewer_suite == self.suite
        ):
            raise ValueError("Reviewer must be a different registered specialist")

def _default_infer(suite: str, question: str, instructions: str) -> dict:
    return lemonade_chat(question, suite, system_instructions=instructions)

def run_pipeline(store: JobStore, request: PipelineRequest, archive: str | Path,
                 *, infer: Callable[[str,str,str],dict] | None = None,
                 acquire: Callable[...,Acquisition] = fetch_source) -> dict:
    """Sequential, explicitly initiated, durable research. No silent web search.

    Stages: approved download -> passage index -> specialist structured JSON
    claim proposals -> lexical candidate matching -> optional peer assessment.
    Failures remain recorded in job store; partial archive acquisitions persist.
    """
    request.validate()
    infer = infer or _default_infer
    job_id = store.submit(Mission(request.suite, request.question, request.approved_scope))
    store.transition(job_id, "queued", "running")
    result = {"schema":"surveyor.pipeline.v0", "job_id":job_id,
              "suite":request.suite, "question":request.question,
              "sources":[], "claims":[], "review_status":"not_reviewed"}
    try:
        passages = []
        for url in request.source_urls:
            item = acquire(url, archive, approved_hosts=request.approved_hosts)
            result["sources"].append(asdict(item))
            passages.extend(index_acquisition(archive,item))
        # Bounded context. Model can see the exact local passages, not claim web access.
        excerpt = [{"passage_id":p.passage_id,"text":p.text,"source_url":p.source_url}
                   for p in passages[:20]]
        question = (request.question + "\n\nRetrieved offline evidence passages (NOT fact-checked):\n"
                    + json.dumps(excerpt,ensure_ascii=False)
                    + '\n\nReturn ONLY JSON: {"claims":[{"statement":"...","geographic_context":"","temporal_context":"","uncertainty":""}]}. '
                      "Do not invent citations; output up to 12 claims limited to your discipline.")
        response = infer(request.suite,question,system_prompt(request.suite,request.approved_scope))
        if not isinstance(response,dict) or not isinstance(response.get("response"),str):
            raise ValueError("Invalid specialist inference response")
        result["raw_response"] = response["response"]
        result["model"] = response.get("model","")
        claims = parse_claim_drafts(response["response"],request.suite,max_claims=12)
        for claim in claims:
            candidates = candidate_passages(claim.statement,passages)
            entry = {"draft":asdict(claim),"candidates":candidates,
                     "verification_status":"unverified","peer_review":None}
            if request.reviewer_suite is not None:
                packet = cross_agent_review_packet(claim,request.reviewer_suite,candidates)
                peer_prompt = (json.dumps(packet,ensure_ascii=False)
                    + '\nReturn ONLY JSON {"assessment":"supported|contradicted|insufficient|disputed","rationale":"..."}. '
                      "This is a proposed peer assessment, not authoritative verification.")
                peer = infer(request.reviewer_suite,peer_prompt,
                             system_prompt(request.reviewer_suite,request.approved_scope))
                if not isinstance(peer,dict) or not isinstance(peer.get("response"),str):
                    raise ValueError("Invalid peer response")
                assessment = json.loads(peer["response"])
                if (not isinstance(assessment,dict) or set(assessment)!={"assessment","rationale"}
                    or assessment["assessment"] not in {"supported","contradicted","insufficient","disputed"}
                    or not isinstance(assessment["rationale"],str) or not assessment["rationale"].strip()):
                    raise ValueError("Malformed peer assessment")
                entry["peer_review"] = {"suite":request.reviewer_suite,
                    "assessment":assessment["assessment"],"rationale":assessment["rationale"],
                    "status":"model_proposal_only"}
            if request.vetting_enabled:
                def assess(packet):
                    prompt = (json.dumps(packet, ensure_ascii=False)
                              + '\\nReturn ONLY JSON {"assessment":"supported|contradicted|insufficient|disputed","rationale":"..."}. '
                                "If supplied evidence is absent or insufficient, answer insufficient.")
                    model_result = infer(request.reviewer_suite, prompt,
                                         system_prompt(request.reviewer_suite, request.approved_scope))
                    if not isinstance(model_result, dict) or not isinstance(model_result.get("response"), str):
                        raise ValueError("Invalid vetting model response")
                    return json.loads(model_result["response"])
                # No autonomous browsing or unseen retrieval; source-backed review
                # remains bounded to operator-approved passages.
                entry["vetting"] = vet_claim(asdict(claim), candidates, assessor=assess,
                                            policy=VettingPolicy(max_investigations=0))
                AuditLog(Path(archive) / "vetting-audit.jsonl").append(
                    {"event_type":"claim_vetting", "job_id":job_id,
                     "claim":asdict(claim), "result":entry["vetting"]})
            result["claims"].append(entry)
        result["status"]="completed"
        store.transition(job_id,"running","completed",result=result)
        return result
    except Exception as exc:
        store.transition(job_id,"running","failed",error=str(exc),
                         result=result)
        raise
