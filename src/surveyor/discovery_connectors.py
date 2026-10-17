"""Offline, operator-provided discovery manifest. No network access."""
from pathlib import Path
import json
from .discovery import DiscoveryHit

def manifest_connector(path: str | Path, provider: str):
    """Read candidate records prepared offline; no source is presumed verified."""
    path = Path(path)
    def search(query: str, limit: int) -> list[DiscoveryHit]:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, list) or len(data) > 200:
            raise ValueError("Manifest must contain no more than 200 objects")
        rows = []
        for entry in data:
            if not isinstance(entry, dict) or not set(entry) <= set(DiscoveryHit.__dataclass_fields__):
                raise ValueError("Invalid discovery manifest entry")
            hit = DiscoveryHit(**entry)
            hit.validate()
            if hit.provider == provider:
                rows.append(hit)
        return rows[:200]
    return search
