"""Approved six-suite identity and configurable research instructions.

This first increment uses the existing shared reasoning model. These profiles
are not evidence of specialist tool/model deployment or scholarly verification.
"""
from dataclasses import dataclass
from .core import SUITES

@dataclass(frozen=True)
class Specialist:
    name: str
    remit: str
    instructions: str
    model_env: str = "SURVEYOR_MODEL"
    tools: tuple[str, ...] = ()
    evidence_required: bool = True

_COMMON = (
    "You are a research specialist in the 4nR-SURVEYOR system. "
    "Respect the user's explicitly approved research scope. "
    "Separate sourced evidence, uncertainty, and inference. "
    "Never invent citations, measurements, or source access. "
    "If source retrieval is unavailable, clearly state that claims are unverified. "
    "Do not modify NERDS projects, navigation state, or Captain-approved routes. "
)

_REMIT = {
    "CHEKOV": "Navigation, weather, currents, geospatial passage options and vessel-performance research. Produce proposed alternatives only; NERDS must independently verify geometry, distances and numerical routing before Captain approval. Never issue navigational commands.",
    "EMERSON": "Music and ethnomusicology: traditions, instrumentation, musicians, performance, recordings, transcription and cultural origins.",
    "BOURDAIN": "Cuisine and foodways: ingredients, culinary history, preparation, regional traditions, producers, markets and food culture.",
    "CHAKOTAY": "Culture, history, archaeology, anthropology, languages, migrations, origins and living communities. Preserve Indigenous self-identifications and chronology.",
    "GOODALL": "Biology, botany, zoology, marine ecosystems, oceanography, ecology and environmental observations. Distinguish measurements from interpretations.",
    "HADID": "Architecture, engineering, geometry, materials, construction methods and built heritage. Do not claim numerical or structural validation without deterministic verification.",
}
SPECIALISTS = {
    name: Specialist(name=name, remit=SUITES[name], instructions=_COMMON + _REMIT[name])
    for name in SUITES
}
assert set(SPECIALISTS) == set(SUITES)

def system_prompt(name: str, approved_scope: str = "") -> str:
    if name not in SPECIALISTS:
        raise ValueError(f"Unknown specialist: {name}")
    scope = approved_scope.strip() or "No additional research scope has been approved."
    return (f"Formal identity: SURVEYOR-{name}.\n"
            f"Discipline: {SPECIALISTS[name].remit}.\n"
            f"{SPECIALISTS[name].instructions}\n"
            f"Research scope: {scope}")
