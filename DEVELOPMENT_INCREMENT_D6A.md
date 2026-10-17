# D6A — Shared discovery engine

Implemented on the SURVEYOR development branch:
- Six-child, provider-specific discovery registries, including the requested YouTube, Bandcamp, Facebook, Instagram, culinary, university and architectural publication targets.
- Common `DiscoveryHit` structure for resources, people, organisations, video, publications and channels.
- Bounded search requests, safe HTTPS URL field validation, deduplication and lexical ranking.
- Provenance-preserving local JSON report archiving with `discovery_only` status.
- Offline manifest connector for exercising real result data without pretending that YouTube/Instagram/Bandcamp APIs are operational.
- Eight automated tests.

**D6A is the data contract and offline discovery runner only.** No live internet API connectors or social-platform scraping, no autonomous source acquisition and no independent vetting of findings. A search result does not demonstrate that source contents have been accessed.

Example manifest file `research_candidates.json`:
```json
[
  {"provider":"youtube","url":"https://www.youtube.com/watch?v=EXAMPLE","title":"Example music source","kind":"video","creator":"Example performer","geographic_context":"Cape Verde"}
]
```
Replace placeholder URL with an actual operator-identified source. Do not treat unverified metadata as fact.

Next: real provider connectors starting with authorised APIs or publisher-supported discovery interfaces; then explicitly approved acquisition, evidentiary vetting, and an offline/online fallback policy. No FWaS email, Entra identity or NERDS dependency.
