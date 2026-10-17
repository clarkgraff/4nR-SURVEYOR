"""Structured evidence records. Source references are NOT proof of verification.

An agent may suggest source URLs, but only an independent acquisition/review
workflow may mark a claim verified. This module never accesses the network.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from urllib.parse import urlsplit

STATUSES = frozenset({"unverified", "source_attached", "contested", "reviewed"})
KINDS = frozenset({"document", "measurement", "interpretation", "model_inference"})

def _clean(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value.strip()

@dataclass(frozen=True)
class SourceReference:
    identifier: str
    title: str
    publisher: str = ""
    retrieved_utc: str | None = None
    licence: str = ""
    evidence_excerpt: str = ""
    acquisition_status: str = "suggested"

    def __post_init__(self) -> None:
        _clean(self.identifier, "source identifier")
        _clean(self.title, "source title")
        if self.acquisition_status not in {"suggested", "retrieved", "reviewed"}:
            raise ValueError("Invalid acquisition status")
        if self.identifier.startswith(("http:", "https:")):
            p = urlsplit(self.identifier)
            if p.scheme != "https" or not p.hostname or p.username or p.password:
                raise ValueError("Web source identifiers must be safe HTTPS URLs")
        if self.acquisition_status in {"retrieved", "reviewed"} and not self.retrieved_utc:
            raise ValueError("Retrieved sources require acquisition timestamp")

@dataclass(frozen=True)
class ResearchClaim:
    statement: str
    suite: str
    evidence_kind: str = "model_inference"
    verification_status: str = "unverified"
    source_ids: tuple[str, ...] = ()
    geographic_context: str = ""
    temporal_context: str = ""
    uncertainty: str = ""

    def __post_init__(self) -> None:
        from .core import SUITES
        _clean(self.statement, "claim")
        if self.suite not in SUITES:
            raise ValueError("Invalid suite")
        if self.evidence_kind not in KINDS or self.verification_status not in STATUSES:
            raise ValueError("Invalid kind or status")
        if self.verification_status == "reviewed":
            raise ValueError("Model-facing claim construction cannot assert reviewed status")
        if self.verification_status == "source_attached" and not self.source_ids:
            raise ValueError("Source-attached claim requires sources")

@dataclass
class ResearchPackage:
    suite: str
    question: str
    raw_response: str
    model: str = ""
    claims: list[ResearchClaim] = field(default_factory=list)
    sources: list[SourceReference] = field(default_factory=list)
    schema_version: str = "surveyor.evidence.v0"
    recorded_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> None:
        from .core import SUITES
        if self.suite not in SUITES:
            raise ValueError("Invalid package suite")
        _clean(self.question, "question")
        if not isinstance(self.raw_response, str):
            raise ValueError("Raw response must be text")
        ids = [s.identifier for s in self.sources]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate source identifiers")
        for claim in self.claims:
            if claim.suite != self.suite:
                raise ValueError("Cross-suite claim in wrong package")
            if set(claim.source_ids) - set(ids):
                raise ValueError("Claim references missing source")
        if self.schema_version != "surveyor.evidence.v0":
            raise ValueError("Unsupported evidence schema")

    def export(self) -> dict:
        self.validate()
        data = asdict(self)
        data["content_sha256"] = sha256(
            json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        return data

def from_inference(suite: str, question: str, output: dict) -> ResearchPackage:
    """Preserve raw inference without hallucinating claim segmentation or citations."""
    raw = output.get("response")
    if not isinstance(raw, str):
        raise ValueError("Inference response is not text")
    pkg = ResearchPackage(suite=suite, question=question, raw_response=raw,
                          model=str(output.get("model", "")))
    pkg.validate()
    return pkg
