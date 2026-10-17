"""Structured claim drafts and explicit review records; no automatic truth certification."""
from dataclasses import dataclass,asdict
from datetime import datetime,timezone
import json
from pathlib import Path
from .core import SUITES

@dataclass(frozen=True)
class ClaimDraft:
    statement:str
    suite:str
    geographic_context:str=""
    temporal_context:str=""
    uncertainty:str=""

def parse_claim_drafts(raw:str,suite:str,*,max_claims:int=30)->list[ClaimDraft]:
    """Read structured model JSON; refuse unrecognised fields and claimed verification."""
    if suite not in SUITES or not 1<=max_claims<=100:raise ValueError("Invalid suite or claim limit")
    document=json.loads(raw)
    if not isinstance(document,dict) or set(document)!={"claims"} or not isinstance(document["claims"],list):
        raise ValueError("Expected JSON object containing claims array")
    if len(document["claims"])>max_claims:raise ValueError("Too many claims")
    result=[]
    fields={"statement","geographic_context","temporal_context","uncertainty"}
    for item in document["claims"]:
        if not isinstance(item,dict) or not set(item)<=fields:raise ValueError("Unrecognised claim fields")
        statement=item.get("statement")
        if not isinstance(statement,str) or not statement.strip():raise ValueError("Missing claim")
        context={name:item.get(name,"") for name in fields-{"statement"}}
        if not all(isinstance(v,str) for v in context.values()):raise ValueError("Nontext claim context")
        result.append(ClaimDraft(statement.strip(),suite,**context))
    return result

def cross_agent_review_packet(claim:ClaimDraft,reviewer_suite:str,candidates:list[dict])->dict:
    if reviewer_suite not in SUITES or reviewer_suite==claim.suite:raise ValueError("Distinct registered reviewer suite required")
    return {"schema":"surveyor.review-request.v0","claim":asdict(claim),
            "reviewer_suite":reviewer_suite,"candidate_passages":candidates,
            "instructions":"Assess passage text for support, contradiction or insufficiency. Propose an assessment only; never certify truth.",
            "review_status":"awaiting_review"}

def record_human_review(path,claim:ClaimDraft,reviewer:str,decision:str,rationale:str,passage_ids:list[str])->dict:
    if decision not in {"supported","contradicted","insufficient","disputed"}:raise ValueError("Invalid review decision")
    if not reviewer.strip() or not rationale.strip():raise ValueError("Reviewer and rationale required")
    event={"schema":"surveyor.human-review.v0","claim":asdict(claim),"reviewer":reviewer,
           "decision":decision,"rationale":rationale,"passage_ids":passage_ids,
           "reviewed_utc":datetime.now(timezone.utc).isoformat()}
    with Path(path).open("a",encoding="utf-8") as file:file.write(json.dumps(event,ensure_ascii=False)+"\n")
    return event
