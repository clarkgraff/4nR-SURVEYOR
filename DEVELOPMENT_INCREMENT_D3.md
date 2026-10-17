# Increment D3 — Integrated research pipeline (initial)

D3 introduces an explicitly invoked Python pipeline API in `surveyor.pipeline`.

- `PipelineRequest` fixes the requesting suite, scope, approved URLs and host list, and optional independent peer-review suite.
- `run_pipeline` executes approved acquisition, local indexing, specialist structured claim drafting, lexical evidence candidates and optional model peer-assessment, with durable SQLite job completion/failure records.
- All claims remain **unverified**. Lexical matches are `candidate_only`; peer review is `model_proposal_only`; neither confers scholarly or operational approval.
- No automatic web searches, self-selected hosts, production DNS-pinned egress, NERDS integration or human review UI.
- Human review recording remains separately available from D2.
- This is a callable Python API, not yet a CLI command or network service. Live source acquisition is not yet authorised as an unattended workflow.
- A bounded 20-passage context is supplied; excess indexed passages are not currently reranked. No semantic recall or robust source-to-claim entailment yet.

## Local tests

```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
$env:PYTHONPATH = "src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compilation failed" }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
```

Expected total: **38** tests, subject to actual GMKtec validation. Next: make source retrieval transport production-safe, add CLI/API, persistence and source verification review controls.
