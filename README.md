# 4nR-SURVEYOR SUITE

Locally operated AI research, orchestration & evidence system for *Faire Wind & Song*.

**System:** MOS — Marine Operations Suite comprises two distinct applications:

- **NERDS — Navigation & Expedition Research Discovery Suite**: Captain-facing geographic discovery, expedition planning, route validation & mission control. Source code is maintained in its own repository: [NERDS_CODEX](https://github.com/clarkgraff/NERDS_CODEX).
- **4nR-SURVEYOR**: Independent AI gatekeeper/orchestrator managing six specialised research agents. This repository contains the SURVEYOR requirements and design documentation. It does **not** constitute a completed implementation.

## Six specialist agents

| Agent | Discipline |
|---|---|
| SURVEYOR-CHEKOV | Navigation, weather, currents & voyage intelligence |
| SURVEYOR-EMERSON | Music & ethnomusicology |
| SURVEYOR-BOURDAIN | Cuisine & foodways |
| SURVEYOR-CHAKOTAY | Culture, history, archaeology, anthropology & languages |
| SURVEYOR-GOODALL | Biology, ecology, oceanography & environmental science |
| SURVEYOR-HADID | Architecture, engineering & built heritage |

## Status & controlling documents

Documentation is separated from executable source code. Candidate models and tools are **under consideration**, not automatically installed, licensed for commercial use, or benchmarked on the vessel's hardware.

- [Consolidated scope — v2.4 source transcription](docs/SURVEYOR_Scope_v2.4_transcription.md) (full archived text from the approved scope; historic nomenclature appears verbatim)
- [Agent roster](agents/README.md)
- [Model evaluation matrix](docs/MODEL_EVALUATION.md)
- [NERDS interface boundary](docs/NERDS_INTEGRATION.md)
- [Implementation & evidence status](docs/STATUS.md)

**Document precedence:** The more recent *20261016_NERDS_4nR-SURVEYOR_Consolidated_Scope_v2.5_Referenced.docx* is the latest consolidated manuscript in the project working files; v2.4 is preserved here as a source transcription, pending an exact v2.5 export. Where earlier text says SURVEYOR is “within NERDS”, the later agreed boundary is **two independent applications**. The latest adopted expansion of NERDS is “Navigation & Expedition Research Discovery Suite”.

## Development philosophy

**Carbon–Silicon Collab:** AI investigates, analyses, calculates & recommends. Humans conceptualise, design, evaluate, decide & act. The Captain has final authority for vessel operations. No model output may automatically become a navigational command.

**Offline-first by design:** A local model & evidence stack reduces dependence on maritime satellite traffic; connected services remain available for acquisition, updates and research.

See the linked scope for the authoritative detailed requirements, classifications, open engineering decisions, acceptance tests and candidate register.
