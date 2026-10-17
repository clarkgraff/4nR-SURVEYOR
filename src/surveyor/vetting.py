"""D5 parent-controlled, bounded claim vetting. No self-certification of truth."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Callable

_DECISIONS = frozenset({"supported", "contradicted", "insufficient", "disputed"})
_ACTIONS = frozenset({"retain_for_review", "investigate_further", "propose_correction", "escalate_dispute"})

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass(frozen=True)
class VettingPolicy:
    max_investigations: int = 2
    min_distinct_sources: int = 2
    def __post_init__(self):
        if not (0 <= self.max_investigations <= 5 and 1 <= self.min_distinct_sources <= 5):
            raise ValueError("Vetting budget outside bounded development limits")

def _source_ids(candidates: list[dict]) -> list[str]:
    return sorted({c["source_url"] for c in candidates
                   if isinstance(c, dict) and isinstance(c.get("source_url"), str)
                   and c.get("verification_status") == "candidate_only"})

def _validate_assessment(value: dict) -> dict:
    if not isinstance(value, dict) or set(value) != {"assessment", "rationale"}:
        raise ValueError("Malformed assessment")
    if value["assessment"] not in _DECISIONS or not isinstance(value["rationale"], str) or not value["rationale"].strip():
        raise ValueError("Invalid assessment")
    return value

def vet_claim(claim: dict, candidates: list[dict], *, assessor: Callable[[dict], dict],
              investigate: Callable[[dict, int], list[dict]] | None = None,
              policy: VettingPolicy = VettingPolicy()) -> dict:
    """Challenge a claim with available candidate passages and optional bounded investigation.

    Assessments, even when labelled supported, remain machine proposals. No
    downloaded material is considered independently trustworthy by this function.
    """
    if not isinstance(claim, dict) or not isinstance(claim.get("statement"), str) or not claim["statement"].strip():
        raise ValueError("Invalid claim")
    evidence = list(candidates)
    history = []
    for attempt in range(policy.max_investigations + 1):
        packet = {"claim": claim, "candidate_passages": evidence,
                  "source_ids": _source_ids(evidence), "round": attempt,
                  "instruction": "Assess support, contradictions and gaps. No automatic verification."}
        evaluation = _validate_assessment(assessor(packet))
        independent_count = len(packet["source_ids"])
        history.append({"round": attempt, "assessment": evaluation,
                        "distinct_source_candidates": independent_count,
                        "recorded_utc": _utc()})
        if evaluation["assessment"] == "supported" and independent_count >= policy.min_distinct_sources:
            action = "retain_for_review"
            break
        if evaluation["assessment"] == "contradicted":
            action = "propose_correction"
            break
        if evaluation["assessment"] == "disputed":
            action = "escalate_dispute"
            break
        if attempt >= policy.max_investigations or investigate is None:
            action = "investigate_further"
            break
        additional = investigate(packet, attempt + 1)
        if not isinstance(additional, list):
            raise ValueError("Investigator must return passage candidates")
        current = {p.get("passage_id") for p in evidence if isinstance(p, dict)}
        for passage in additional:
            if not isinstance(passage, dict) or not isinstance(passage.get("passage_id"), str):
                raise ValueError("Malformed investigation passage")
            if passage["passage_id"] not in current:
                evidence.append(passage)
                current.add(passage["passage_id"])
    if action not in _ACTIONS:
        raise ValueError("Invalid next action")
    return {"schema": "surveyor.vetting.v0", "claim": claim,
            "candidate_passages": evidence, "assessments": history,
            "next_action": action, "verification_status": "unverified",
            "human_approval_required": True}

class AuditLog:
    """Append-only JSONL event stream with hash-linked integrity indicators."""
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, event: dict) -> dict:
        if not isinstance(event, dict):
            raise ValueError("Audit event must be an object")
        previous = "0" * 64
        if self.path.exists():
            records = self.path.read_text(encoding="utf-8").splitlines()
            if records:
                previous = json.loads(records[-1])["event_sha256"]
        entry = {"recorded_utc": _utc(), "previous_sha256": previous, "event": event}
        fingerprint = sha256(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        entry["event_sha256"] = fingerprint
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def validate(self) -> int:
        previous = "0" * 64
        if not self.path.exists():
            return 0
        count = 0
        for line in self.path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            actual = record.pop("event_sha256")
            digest = sha256(json.dumps(record, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
            if actual != digest or record["previous_sha256"] != previous:
                raise ValueError("Audit chain integrity failure")
            previous = actual
            count += 1
        return count

@dataclass(frozen=True)
class ImprovementProposal:
    failure_id: str
    hypothesis: str
    candidate_change: str
    baseline_metric: str
    proposed_benchmark: str
    status: str = "proposed"

    def __post_init__(self):
        if self.status != "proposed":
            raise ValueError("No automated improvement promotion")
        for value in (self.failure_id, self.hypothesis, self.candidate_change,
                      self.baseline_metric, self.proposed_benchmark):
            if not value.strip():
                raise ValueError("Incomplete improvement proposal")

def register_improvement(log: AuditLog, proposal: ImprovementProposal) -> dict:
    return log.append({"event_type": "improvement_proposal", "proposal": asdict(proposal),
                       "promotion_authorised": False})
