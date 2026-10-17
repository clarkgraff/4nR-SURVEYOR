"""D6A discovery contracts and bounded, local candidate ranking.

Discovery is independent of acquisition and verification. Connectors must be
explicitly selected; this module does not scrape websites or call model tools.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Callable
from urllib.parse import urlsplit, urlunsplit
from .specialists import SPECIALISTS

SOURCES = {
    "CHEKOV": ("maritime", "university", "government", "youtube"),
    "EMERSON": ("youtube", "facebook", "instagram", "bandcamp", "university"),
    "BOURDAIN": ("youtube", "facebook", "instagram", "allrecipes", "food_network"),
    "CHAKOTAY": ("youtube", "instagram", "facebook", "university"),
    "GOODALL": ("youtube", "instagram", "facebook", "university"),
    "HADID": ("youtube", "instagram", "facebook", "architecture_publication"),
}

@dataclass(frozen=True)
class DiscoveryRequest:
    suite: str
    query: str
    providers: tuple[str, ...]
    approved_scope: str = ""
    max_results: int = 20

    def validate(self):
        if self.suite not in SPECIALISTS or not self.query.strip():
            raise ValueError("Unknown suite or blank search")
        if not (1 <= self.max_results <= 50):
            raise ValueError("Invalid result limit")
        if not self.providers or len(self.providers) != len(set(self.providers)):
            raise ValueError("Distinct providers required")
        if any(p not in SOURCES[self.suite] for p in self.providers):
            raise ValueError("Provider not allowed for this suite")

@dataclass(frozen=True)
class DiscoveryHit:
    provider: str
    url: str
    title: str
    description: str = ""
    creator: str = ""
    kind: str = "resource"
    geographic_context: str = ""
    published_date: str = ""

    def validate(self):
        parsed = urlsplit(self.url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Discovery URL must be a public HTTPS URL without credentials")
        if self.kind not in {"resource", "person", "organisation", "video", "publication", "channel"}:
            raise ValueError("Unsupported discovery kind")
        if not self.title.strip():
            raise ValueError("Missing title")

def _canonical(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(),
                       parsed.path.rstrip("/") or "/", parsed.query, ""))

def rank_hits(request: DiscoveryRequest, hits: list[DiscoveryHit]) -> list[dict]:
    """Lexical discovery ranking only; score is not authority or veracity."""
    request.validate()
    terms = set(re.findall(r"\b\w{3,}\b", (request.query + " " + request.approved_scope).casefold()))
    unique = {}
    for hit in hits:
        hit.validate()
        if hit.provider not in request.providers:
            raise ValueError("Result from unrequested provider")
        key = _canonical(hit.url)
        haystack = (hit.title + " " + hit.description + " " +
                    hit.creator + " " + hit.geographic_context).casefold()
        overlap = len(terms & set(re.findall(r"\b\w{3,}\b", haystack)))
        row = {**asdict(hit), "relevance_tokens": overlap,
               "evidence_status": "discovery_only", "approved_for_acquisition": False}
        if key not in unique or overlap > unique[key]["relevance_tokens"]:
            unique[key] = row
    return sorted(unique.values(), key=lambda h: (-h["relevance_tokens"], h["url"]))[:request.max_results]

def discover(request: DiscoveryRequest, connectors: dict[str, Callable[[str, int], list[DiscoveryHit]]]) -> dict:
    """Invoke only explicitly installed connectors, rejecting unsupported providers."""
    request.validate()
    results = []
    for provider in request.providers:
        if provider not in connectors:
            raise ValueError("Discovery connector not installed: " + provider)
        batch = connectors[provider](request.query, request.max_results)
        if not isinstance(batch, list) or len(batch) > 200 or any(not isinstance(h, DiscoveryHit) for h in batch):
            raise ValueError("Malformed provider results")
        results.extend(batch)
    return {"schema": "surveyor.discovery.v0", "suite": request.suite,
            "query": request.query, "providers": list(request.providers),
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "results": rank_hits(request, results),
            "verification_status": "not_verified"}

def save_report(report: dict, archive: str | Path) -> Path:
    """Persist discovery as data, not as verified research or auto-acquisition."""
    if report.get("schema") != "surveyor.discovery.v0":
        raise ValueError("Unsupported discovery report")
    import uuid
    root = Path(archive) / "discovery"
    root.mkdir(parents=True, exist_ok=True)
    destination = root / (uuid.uuid4().hex + ".json")
    with destination.open("x", encoding="utf-8") as fp:
        json.dump(report, fp, ensure_ascii=False, indent=2)
    return destination
