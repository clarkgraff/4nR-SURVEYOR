# Approved architecture: NERDS and 4nR-SURVEYOR

**Decision recorded:** 16 October 2026. **Scope:** architecture and development requirements, not an assertion of completed functionality.

## Two distinct applications

**NERDS — Navigation & Expedition Research Discovery Suite** is the **principal front end, user interface and independent algorithmic (non-AI) preliminary-intelligence application** for *Faire Wind & Song*. It must perform as much of its core work as practicable without 4nR-SURVEYOR, an LLM, an inference server or Internet access.

NERDS independently provides:
- World geographic discovery using available structured local datasets, with optional Internet retrieval and updates.
- Preliminary fact gathering, search, structured querying, filters, indexing and rule-based classification.
- Geographic information systems, waypoint/project management, voyage planning and Captain-facing presentation.
- Deterministic or otherwise explicitly specified conventional calculations and algorithms for route geometry, geography, distances, times and validation.
- Source/provenance records for conventional research, clear identification of incomplete or unresolved data, and saved-project operation.
- User-facing requests for deeper research from SURVEYOR and presentation of its evidence and recommendations when available.

**4nR-SURVEYOR** is a **separate advanced AI intelligence and orchestration application**. It performs deeper, more complex, specialist, cross-disciplinary research and interpretation when requested or authorised. It coordinates six logical agents: **CHEKOV, EMERSON, BOURDAIN, CHAKOTAY, GOODALL and HADID**, selecting appropriate local models, specialist analytical tools, research databases and evidence sources.

The SURVEYOR suite may use conventional numerical and scientific software alongside AI models. The term *algorithmic versus AI* describes the intended architectural split; AI itself also uses algorithms.

## Integration and decision boundary

1. NERDS first conducts preliminary **non-AI algorithmic intelligence** and presents findings through its own interface.
2. If further depth, interpretation, complex analysis or specialist capability is warranted, NERDS sends a **structured research request** to SURVEYOR.
3. SURVEYOR coordinates the suitable agent(s), models, databases and tools, performs the investigation, and returns **source-aware findings, alternatives, assumptions and evidence**.
4. NERDS presents these outputs to the user and **independently checks all relevant geographic/numeric route claims** with established software.
5. Human operators review and approve decisions. **The Captain retains navigation and vessel authority.** No SURVEYOR output automatically changes an approved voyage plan.
6. If SURVEYOR is stopped, unavailable or still under development, **NERDS continues to work independently**, including its core projects, preliminary discovery and routing functions.

**Non-AI means no requirement for generative inference to carry out NERDS' core responsibilities.** No hidden dependency on Lemonade/Qwen or the SURVEYOR process is permitted for essential NERDS workflows. An optional connection/test panel in an earlier NERDS prototype is not authority to transfer its essential functions to AI.

## Repositories and marketing identity

- [NERDS_CODEX](https://github.com/clarkgraff/NERDS_CODEX) — active CODEX development repository for NERDS.
- [NERDS](https://github.com/clarkgraff/NERDS) — original/master NERDS repository.
- [4nR-SURVEYOR](https://github.com/clarkgraff/4nR-SURVEYOR) — separate SURVEYOR documentation/application repository.

**MOS — Marine Operations Suite** is *only* the collective marketing identity for the NERDS and 4nR-SURVEYOR applications. MOS is not a third software application, a software module, an independent development stream or a GitHub repository.

Both applications maintain independent codebases, version control, testing, release cycles and the option of operating on separate onboard LAN machines.

## Status

This file formalises the architecture **without asserting that SURVEYOR, its six-agent runtime or the complete interface has already been coded or tested**. Implementations must be assessed against their actual test evidence. The historical v2.4 SURVEYOR scope remains preserved as an unmodified source; where it contains legacy nomenclature or wording implying SURVEYOR is `within NERDS`, this explicit later decision controls the intended separation and division of responsibilities.
