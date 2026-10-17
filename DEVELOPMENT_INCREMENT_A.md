# 4nR-SURVEYOR — Development Increment A (parent foundation)

**Status:** Initial executable scaffolding, not an approved release, not operational navigation software, not six implemented research agents.

## Included
- Separate Python standard-library CLI (does not alter NERDS).
- Exactly six named suite registrations.
- SQLite job persistence with queued/running/completed/failed/cancelled states.
- Explicit single-job dispatch, cancellation/resumption of **queued** jobs only.
- Configurable OpenAI-compatible Lemonade adapter (endpoint/model supplied at runtime).
- Mock-based unit tests; no AI or onboard hardware required.

## Run from repository root

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
python -m surveyor suites
python -m surveyor submit CHEKOV 'Investigate seasonal currents near Saint Peter and Saint Paul Rocks'
python -m surveyor get 1
$env:SURVEYOR_MODEL = '<EXACT INSTALLED MODEL ID>'
python -m surveyor run 1
```

The default Lemonade base URL is `http://127.0.0.1:13305/api/v1` based on the historical handover record; the chat-completions path and exact installed model identifier must be confirmed on the user's current Lemonade version. No live hardware integration has been verified by these unit tests.

## Not yet implemented
- Network API, NERDS integration, authentication and versioned interface schemas.
- Long-running autonomous queues, background workers, concurrent dispatch, safe retry/recovery of running jobs.
- Source acquisition, citations/evidence validation, models/tools per suite, shared knowledge graph, resource budgets.
- Route generation, vector-geometry verification, Captain-facing navigation, environmental sensing.
- Complete timeout, cancellation and telemetry policies; release packaging.

**Next:** validate current Lemonade API/model list and agree interface schema; implement durable worker/recovery and suite-specific task profiles. Nothing here may issue vessel controls or overwrite the Captain-approved route.
