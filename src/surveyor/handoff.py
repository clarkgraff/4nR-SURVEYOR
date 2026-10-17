"""D6C-3: explicit handoff from a reviewed discovery disposition to research.

No hidden downloads. YouTube metadata is not ingested as video evidence.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from urllib.parse import urlsplit
from .core import JobStore, Mission
from .presentation import _load as _load_discovery, present, save_presentation
from .pipeline import PipelineRequest, run_pipeline

@dataclass(frozen=True)
class Handoff:
    presentation_file: str
    source_index: int
    question: str
    suite: str
    original_url: str
    investigation_job: int

def create_handoff(store: JobStore, presentation_file: str | Path, source_index: int,
                   reason: str, *, archive: str | Path) -> dict:
    """Create a QUEUED, traceable job from a previously recorded decision."""
    from .vetting import AuditLog
    doc = json.loads(Path(presentation_file).read_text(encoding="utf-8-sig"))
    if doc.get("schema") != "surveyor.presentation.v0":
        raise ValueError("Invalid presentation")
    if not isinstance(source_index,int) or not 1 <= source_index <= len(doc["sources"]):
        raise ValueError("Invalid source index")
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError("Investigation rationale is required")
    source = doc["sources"][source_index-1]
    # A decision must have been explicitly recorded for this exact item.
    log = AuditLog(Path(archive)/"presentation-decisions.jsonl")
    log.validate()
    entries = Path(log.path).read_text(encoding="utf-8").splitlines() if log.path.exists() else []
    matching = [json.loads(line)["event"] for line in entries
                if (lambda event: event.get("schema")=="surveyor.user-disposition.v0"
                    and event.get("presentation_id")==doc["presentation_id"]
                    and event.get("source_index")==source_index
                    and event.get("source_url")==source["url"]
                    and event.get("action")=="investigate_further")(json.loads(line)["event"])]
    if not matching:
        raise ValueError("Explicit investigate_further decision not found")
    question = reason.strip() + "\nDiscovered reference (METADATA ONLY): " + source["url"]
    mission = Mission(doc["suite"],question,"User-directed research follow-up; external source content not approved")
    job = store.submit(mission)
    report={"schema":"surveyor.investigation-handoff.v0","job_id":job,
            "presentation_id":doc["presentation_id"],"source_index":source_index,
            "original_url":source["url"],"suite":doc["suite"],"question":question,
            "status":"queued","source_content_status":"not_acquired",
            "acquisition_approved":False,"human_review_required":True}
    AuditLog(Path(archive)/"investigation-handoffs.jsonl").append(report)
    return report

def execute_handoff(store: JobStore, job_id: int, *, archive: str | Path,
                    reviewer: str | None = None, infer=None) -> dict:
    """Execute queued follow-up with no source downloads; present result for review."""
    from .vetting import AuditLog
    log=AuditLog(Path(archive)/"investigation-handoffs.jsonl")
    log.validate()
    events=[json.loads(line)["event"] for line in Path(log.path).read_text(encoding="utf-8").splitlines()]
    handoffs=[event for event in events if event.get("schema")=="surveyor.investigation-handoff.v0"
              and event.get("job_id")==job_id]
    if len(handoffs)!=1:
        raise ValueError("Expected one registered handoff job")
    handoff=handoffs[0]
    job=store.get(job_id)
    if job["status"]!="queued" or job["suite"]!=handoff["suite"]:
        raise ValueError("Handoff job must be queued and match assigned suite")
    store.transition(job_id,"queued","running")
    try:
        # Use existing pipeline in a distinct durable job. The handoff job tracks it.
        request=PipelineRequest(job["suite"],job["question"],job["approved_scope"],
                                reviewer_suite=reviewer,vetting_enabled=bool(reviewer))
        result=run_pipeline(store,request,archive,infer=infer)
        # Locate immutable original presentation by ID.
        original=Path(archive)/"presentations"/(handoff["presentation_id"]+".json")
        if not original.exists():
            raise ValueError("Original presentation not found in archive")
        original_report=json.loads(original.read_text(encoding="utf-8-sig"))
        derived=present(original_report["discovery_file"],pipeline_result=result)
        saved=save_presentation(derived,archive)
        outcome={"schema":"surveyor.investigation-completion.v0","handoff_job_id":job_id,
                 "research_job_id":result["job_id"],"presentation_path":str(saved),
                 "status":"completed","verification_status":"unverified"}
        store.transition(job_id,"running","completed",result=outcome)
        log.append(outcome)
        return outcome
    except Exception as exc:
        store.transition(job_id,"running","failed",error=str(exc))
        raise
