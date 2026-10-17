# Increment C — Research evidence foundation

**Status:** Committed on the development branch; local GMKtec validation pending.

## Delivered
- `surveyor.evidence.v0` structured package with original model response, optional individually recorded research claims, source identifiers, geographic/temporal context, timestamps and a content SHA-256.
- Source lifecycle: `suggested`, `retrieved`, `reviewed`. A URL suggested by a model is never treated as an acquired document.
- Claim status and source linkage validation; reject missing source records, cross-suite claims and model-generated `reviewed` claims.
- Multi-suite research jobs save an initial empty-claims/empty-sources evidence package alongside the original unverified model output; claim extraction and corroboration are deliberately NOT simulated.
- Seven new unit tests. Total expected test count after sync: 17.

## Limitations
This code has **no** external source retrieval, independent review, claim extraction, scholarly search, licensing checks, model-evidence scoring or verified research ability. SHA-256 only checks data integrity; it does not prove factual truth. Source metadata is a record design, not evidence that a source has been read.

## Later development gates
1. Source acquisition & licence controls, with provenance, source bytes/hashes and retrieval timestamps.
2. Typed model output/claim extraction with malformed-output recovery.
3. Independent corroboration and reviewer approval transitions.
4. Shared cross-suite canonical entities and research classifications.
5. Versioned authenticated API, background work and NERDS integration.

## Local verification after next successful synchronisation

```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
$env:PYTHONPATH = "src"
python -m compileall -q src tests
python -m unittest discover -s tests -v
```

Important: the previous local edit to `src/surveyor/core.py` may prevent pulling. Inspect `git status` before synchronising; do not discard local changes without checking them.
