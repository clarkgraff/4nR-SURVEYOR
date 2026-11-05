"""CHAKOTAY historical and cultural research dossier assembly.

Consumes existing GAIA pipeline and discovery outputs.
Does not acquire sources, infer facts, verify claims, or approve research.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from .core import utcnow

THEMES = frozenset({
    "history",
    "archaeology",
    "anthropology",
    "culture",
    "language",
    "migration",
    "living_communities",
    "unclassified",
})


def build_dossier(
    destination: str,
    pipeline_result: dict,
    *,
    discovery_report: dict | None = None,
    themes: dict[int, str] | None = None,
) -> dict:
    """Build an unverified dossier from CHAKOTAY-only GAIA outputs.

    Theme assignments are supplied explicitly. No lexical classification
    is presented as historical or anthropological understanding.
    """
    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination is required")

    if not isinstance(pipeline_result, dict):
        raise ValueError("Pipeline result must be an object")

    if (
        pipeline_result.get("schema") != "surveyor.pipeline.v0"
        or pipeline_result.get("suite") != "CHAKOTAY"
        or pipeline_result.get("status") != "completed"
    ):
        raise ValueError("Expected completed CHAKOTAY pipeline result")

    claims = pipeline_result.get("claims")
    if not isinstance(claims, list):
        raise ValueError("Invalid pipeline claims")

    themes = themes if themes is not None else {}
    if not isinstance(themes, dict):
        raise ValueError("Theme assignments must be a dictionary")
    if any(
        not isinstance(index, int)
        or isinstance(index, bool)
        or not 1 <= index <= len(claims)
        or theme not in THEMES
        for index, theme in themes.items()
    ):
        raise ValueError("Invalid claim index or theme")

    entries = []
    chronology = []

    for index, item in enumerate(claims, start=1):
        if not isinstance(item, dict):
            raise ValueError("Invalid claim entry")

        draft = item.get("draft")
        candidates = item.get("candidates", [])

        if (
            not isinstance(draft, dict)
            or not isinstance(draft.get("statement"), str)
            or not draft["statement"].strip()
            or not isinstance(candidates, list)
        ):
            raise ValueError("Malformed claim or evidence candidates")

        if draft.get("suite", "CHAKOTAY") != "CHAKOTAY":
            raise ValueError("Cross-specialist claim rejected")

        if any(
            not isinstance(candidate, dict)
            or candidate.get("verification_status") != "candidate_only"
            or not isinstance(candidate.get("source_url"), str)
            or not isinstance(candidate.get("passage_id"), str)
            for candidate in candidates
        ):
            raise ValueError("Invalid candidate passage provenance")

        entry = {
            "index": index,
            "theme": themes.get(index, "unclassified"),
            "statement": draft["statement"],
            "geographic_context": draft.get("geographic_context", ""),
            "temporal_context": draft.get("temporal_context", ""),
            "uncertainty": draft.get("uncertainty", ""),
            "candidate_passages": candidates,
            "verification_status": "unverified",
            "editorial_status": "pending_review",
        }
        entries.append(entry)

        if entry["temporal_context"]:
            chronology.append({
                "claim_index": index,
                "temporal_context": entry["temporal_context"],
                "statement": entry["statement"],
                "verification_status": "unverified",
            })

    contributors = []

    if discovery_report is not None:
        if (
            not isinstance(discovery_report, dict)
            or discovery_report.get("schema") != "surveyor.discovery.v0"
            or discovery_report.get("suite") != "CHAKOTAY"
            or not isinstance(discovery_report.get("results"), list)
        ):
            raise ValueError("Expected CHAKOTAY discovery report")

        for hit in discovery_report["results"]:
            if not isinstance(hit, dict):
                raise ValueError("Malformed discovery hit")

            if hit.get("kind") not in {"person", "organisation"}:
                continue

            if (
                not isinstance(hit.get("title"), str)
                or not hit["title"].strip()
                or not isinstance(hit.get("url"), str)
                or not hit["url"].startswith("https://")
            ):
                raise ValueError("Malformed contributor candidate")

            contributors.append({
                "name": hit["title"],
                "kind": hit["kind"],
                "url": hit["url"],
                "provider": hit.get("provider", ""),
                "description": hit.get("description", ""),
                "discovery_status": "candidate_only",
                "contact_status": "not_contacted",
                "editorial_status": "pending_review",
            })

    return {
        "schema": "surveyor.chakotay-dossier.v0",
        "suite": "CHAKOTAY",
        "destination": destination.strip(),
        "created_utc": utcnow(),
        "pipeline_job_id": pipeline_result.get("job_id"),
        "research_question": pipeline_result.get("question", ""),
        "claims": entries,
        "chronology": chronology,
        "contributors": contributors,
        "verification_status": "unverified",
        "editorial_status": "pending_review",
        "notes": [
            "Chronology is not independently date-validated or sorted.",
            "Candidate passages are not verified historical evidence.",
            "Contributor discovery does not establish identity or availability.",
            "Human editorial approval is required.",
        ],
    }


def save_dossier(dossier: dict, archive: str | Path) -> Path:
    """Persist a dossier as an immutable, content-addressed JSON file."""
    if (
        not isinstance(dossier, dict)
        or dossier.get("schema") != "surveyor.chakotay-dossier.v0"
        or dossier.get("suite") != "CHAKOTAY"
    ):
        raise ValueError("Invalid CHAKOTAY dossier")

    payload = json.dumps(
        dossier, ensure_ascii=False, sort_keys=True, indent=2
    ).encode("utf-8")

    digest = sha256(payload).hexdigest()
    folder = Path(archive) / "chakotay" / "dossiers"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (digest + ".json")

    try:
        with target.open("xb") as stream:
            stream.write(payload)
    except FileExistsError:
        if target.read_bytes() != payload:
            raise ValueError("Existing dossier content mismatch")

    return target