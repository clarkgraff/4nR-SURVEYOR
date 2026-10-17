# Increment B — Six specialist profiles and research coordination

Status: source committed for local testing; not yet proven on GMKtec.

## Implemented in this branch
- Six named, differentiated specialist instruction profiles: CHEKOV, EMERSON, BOURDAIN, CHAKOTAY, GOODALL and HADID.
- Explicit caller selection of participating suites, no silent model-directed delegation.
- Sequential specialist calls through the existing Lemonade adapter and configured `SURVEYOR_MODEL`.
- A separate durable SQLite job and result record per specialist.
- Failure stops subsequent dispatch; returned batch report indicates partial failure.
- All generated responses retain an unverified evidence label.
- Five additional unit tests for profiles, navigation constraints, multi-suite dispatch, persistence, and failure behaviour.

## Run from PowerShell on development branch

```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
$env:SURVEYOR_MODEL = "Qwen3-30B-A3B-GGUF"
python -m surveyor research "Compare the musical and culinary traditions of Cape Verde. Identify overlap without inventing sources." --suites EMERSON BOURDAIN --scope "Preliminary Cape Verde destination research"
```

The response contains two job IDs. Inspect persisted records using `python -m surveyor get <ID>`.

## Critical boundaries
- No source retrieval, independent fact checking or specialist multimodal models yet.
- No shared knowledge graph, inter-agent evidence synthesis or automatic agent selection yet.
- No background job runner, per-job timeout, cancellation of running inference, or authenticated network API.
- No NERDS route integration or direct vessel control.
- A successful inference demonstrates execution, not factual research quality.

Next increments: evidence retrieval/provenance, versioned API, resource scheduling, durable worker restart recovery and suite-specific tools.
