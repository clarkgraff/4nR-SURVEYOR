"""D6C operator-facing presentation & decision ledger.

Discovery metadata never becomes evidence by presentation or approval.
An approval means accept for downstream consideration, not verified truth.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from .vetting import AuditLog

ACTIONS = frozenset({"approve", "investigate_further", "flag_correct", "save_for_later"})

def _load(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or data.get("schema") != "surveyor.discovery.v0":
        raise ValueError("Expected a SURVEYOR discovery report")
    if not isinstance(data.get("results"), list):
        raise ValueError("Discovery report has invalid results")
    return data

def present(discovery_path: str | Path, *, pipeline_result: dict | None = None) -> dict:
    """Present source links and separately labelled claim drafts, without fabrication."""
    discovery = _load(discovery_path)
    claims = []
    if pipeline_result is not None:
        if pipeline_result.get("schema") != "surveyor.pipeline.v0":
            raise ValueError("Expected SURVEYOR pipeline result")
        if pipeline_result.get("suite") != discovery.get("suite"):
            raise ValueError("Discovery and investigation suites differ")
        for item in pipeline_result.get("claims", []):
            claims.append({"claim": item["draft"], "verification_status": "unverified",
                           "candidates": item.get("candidates", []),
                           "vetting": item.get("vetting"),
                           "peer_review": item.get("peer_review")})
    payload = {"schema": "surveyor.presentation.v0",
               "created_utc": datetime.now(timezone.utc).isoformat(),
               "suite": discovery["suite"], "query": discovery["query"],
               "discovery_file": str(discovery_path),
               "research_job_id": pipeline_result.get("job_id") if pipeline_result else None,
               "sources": [{"index": i + 1, "title": hit["title"],
                            "url": hit["url"], "provider": hit["provider"],
                            "creator": hit.get("creator", ""),
                            "description": hit.get("description", ""),
                            "status": "discovery_only"} for i,hit in enumerate(discovery["results"])],
               "claims": claims,
               "approval_scope": "workflow_disposition_only",
               "research_verification": "not_verified",
               "available_actions": sorted(ACTIONS)}
    payload["presentation_id"] = sha256(json.dumps(payload,sort_keys=True,
                                   ensure_ascii=False).encode("utf-8")).hexdigest()
    return payload

def save_presentation(payload: dict, archive: str | Path) -> Path:
    if payload.get("schema") != "surveyor.presentation.v0":
        raise ValueError("Invalid presentation")
    target = Path(archive) / "presentations" / (payload["presentation_id"] + ".json")
    target.parent.mkdir(parents=True,exist_ok=True)
    # Same presentation can be presented repeatedly; never overwrite.
    if not target.exists():
        with target.open("x",encoding="utf-8") as stream:
            json.dump(payload,stream,indent=2,ensure_ascii=False)
    return target

def record_decision(presentation_path: str | Path, item: int, action: str,
                    operator: str, rationale: str, *, archive: str | Path) -> dict:
    if action not in ACTIONS or not operator.strip() or not rationale.strip():
        raise ValueError("Valid decision, operator, and rationale required")
    presentation = json.loads(Path(presentation_path).read_text(encoding="utf-8-sig"))
    if presentation.get("schema") != "surveyor.presentation.v0":
        raise ValueError("Invalid presentation record")
    if not isinstance(item,int) or not 1 <= item <= len(presentation["sources"]):
        raise ValueError("Item number outside presented sources")
    decision = {"schema":"surveyor.user-disposition.v0", "presentation_id":presentation["presentation_id"],
                "source_index":item, "source_url":presentation["sources"][item-1]["url"],
                "action": action, "operator":operator, "rationale":rationale,
                "verification_status":"not_verified",
                "approved_as_evidence":False}
    AuditLog(Path(archive)/"presentation-decisions.jsonl").append(decision)
    return decision
