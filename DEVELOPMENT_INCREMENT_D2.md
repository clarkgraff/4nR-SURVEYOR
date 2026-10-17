# Increment D2 — Offline document passage indexing & review scaffolding

## Source changes
- Parse previously acquired UTF-8 HTML/plain text/JSON; remove HTML script/style contents.
- Build small stable source-hash-based passage IDs and a persisted passage index.
- Deterministic keyword overlap to suggest source passages. A match is NOT corroboration.
- Parse structured model-produced JSON claim drafts, rejecting unrecognised verification fields.
- Prepare cross-suite review request packets (not automatic review execution).
- Append named human-review decisions with rationales to a JSONL record.

## Limitations
- No reliable natural-language entailment, contradiction detection, semantic index, external scholarly source search, automatic claim extraction invocation, or cross-agent reviewer execution.
- No verified claims are issued automatically. A human review is a recorded assessment, not a proof of truth.
- Indexer accepts current D1 text/plain, text/html and application/json assets; other formats need explicit parsers.
- These modules are not wired into the existing CLI research flow; integration remains the next increment.
- The acquisition module still needs production transport hardening against DNS rebinding; no automated unsupervised acquisition.

## Verification
Ten D2 isolated tests were run in the development environment against lightweight local representations of the existing acquisition record and suite roster. Full repository compatibility and the expected **33 total tests** must be established on the GMKtec using:

```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
$env:PYTHONPATH = "src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compilation failed" }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
```
