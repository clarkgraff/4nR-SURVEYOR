# D5 development status and YouTube research-source requirement

## Current D5 source status
`src/surveyor/vetting.py` and `tests/test_vetting.py` have been committed as the initial parent vetting foundation. They provide bounded reassessment, an audit-chain format, and improvement proposals that cannot self-promote to production. The code is **not yet wired into the main pipeline or CLI**, and no GMKtec validation has been performed. Agent agreement is not independent verification.

## Additional research discovery requirement — YouTube
SURVEYOR is expected to search YouTube as one of its potential discovery sources **across all six suites**, including both audiovisual works and identifiable people/organisations that may matter to the approved research scope. This is a future engineering requirement, not an implemented capability.

- EMERSON: performers, instrumentation, music events and performances.
- BOURDAIN: cooks, culinary practice, suppliers, markets and food traditions.
- CHAKOTAY: communities, language, oral histories and cultural documentary content.
- GOODALL: field footage, marine ecology, wildlife and environmental projects.
- HADID: structures, construction techniques, architects and craftspeople.
- CHEKOV: waterways, ports, maritime operation and condition observations (not navigation authority).

Candidate source interface: authorised YouTube Data API search for video/channel/playlist results, standardised provenance, localisation and source identity. Transcript/caption and actual audiovisual analysis require separate technical/legal evaluation. Do not treat title/description text as verified video contents, and do not download/cache audiovisual content without necessary rights or permissions.

Official references:
- https://developers.google.com/youtube/v3/docs/search/list
- https://developers.google.com/youtube/terms/developer-policies
- https://developers.google.com/youtube/data/reference/rest/v3/captions/list

Do not implement this connector without establishing authentication, API quota budget, metadata retention rules, source licences and acceptance tests. NERDS and Captain operational authority remain unchanged.

## User-directed cross-platform discovery expansion — 17 October 2026

This register preserves the specifically requested discovery channels. They are research-source targets, **not claims of implemented API connectors**.

| Suite | Requested platforms / institutional sources |
|---|---|
| EMERSON | YouTube; Facebook; Instagram; “Garage Band” (wording preserved; identity to confirm) |
| BOURDAIN | YouTube; Facebook; Instagram; Allrecipes; Food Network |
| CHAKOTAY | YouTube; Instagram; Facebook; universities |
| GOODALL | YouTube; Instagram; Facebook; universities |
| HADID | YouTube; Instagram; Facebook; architecture magazines |

**“Garage Band” clarification:** Apple's GarageBand is music-production software rather than a public emerging-artist discovery directory. Bandcamp is a distinct music community and discovery service that may have been intended. Do not silently substitute Bandcamp for the user's original name; confirm before implementing an integration.

**Discovery objectives:** identify relevant people, projects, creators, channels, communities, performances, demonstrations and institutional publications within the user's approved disciplinary, geographic and historical research filters. Record original URL, identity, description, dates, geographic/temporal relevance, evidence type and licence/access conditions. Distinguish inferred relationships from source-supported ones; do not equate social engagement counts with authority. Store or analyse video, images, captions or posts only through permitted interfaces and rights-compatible access.

**CHEKOV:** Current maritime-source discovery scope remains unchanged; no additional platform list was specified in this amendment.

**Implementation gate:** platform APIs, authentication, quotas, permissions and search coverage must be evaluated separately; public browser visibility is not a guarantee of API access. No platform integration is claimed operational by this requirements record.
