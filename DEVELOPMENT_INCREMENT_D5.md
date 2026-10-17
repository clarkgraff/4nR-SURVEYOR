# D5 — Parent-led claim vetting foundation

## Implemented
- `surveyor.vetting.vet_claim`: bounded review orchestration, assessment validation, distinct-source candidate counting, non-authoritative action routing and required human approval.
- `AuditLog`: hash-linked append-only JSONL audit events and integrity check (tamper-evident, **not** tamper-proof or concurrency-safe).
- `ImprovementProposal`: append-only proposed research-method improvements; no automatic promotion of model or policy changes.
- `run_pipeline(... PipelineRequest(... vetting_enabled=True))`: an additional model review against candidate passages and an audit event for each claim.
- `python -m surveyor pipeline ... --reviewer CHAKOTAY --vet` to opt into parent vetting.
- Automated vetting does not label any claim verified and never promotes knowledge to an approved catalogue.

## Important limitations
- The D5 integration uses **zero automatic additional investigations** (`max_investigations=0`): uncorroborated claims receive `investigate_further`. The `vet_claim` core supports a bounded investigation callback, but no live discovery/approved new-source acquisition callback is connected yet.
- The pre-existing optional `--reviewer` step and D5's `--vet` step both invoke review when supplied together. They are separate preliminary opinions, not independent confirmation.
- The source count refers to distinct URLs among **lexically matched candidate passages**. It does not establish source independence, authority, or genuine textual support.
- No automatic source discovery, self-directed search, YouTube/social platform connectors, retrieval quality evaluation or machine-approved self-improvement.
- For online downloads, operator authorisation and production transport hardening remain required. No unattended acquisition.
- Test assertions verify plumbing and safety boundaries with mocks; live-source scholarly accuracy remains untested.

## GMKtec tests
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

Expected count: **55 tests** (42 previous + 9 vetting unit tests + 4 integration tests), pending GMKtec validation.

## Controlled local model test (no new network requests)
```powershell
python -m surveyor pipeline EMERSON "Identify three Cape Verdean musical traditions" --scope "Preliminary research test" --reviewer CHAKOTAY --vet --archive surveyor-archive
```
With no approved evidence sources, the expected disposition is `investigate_further`, even if the model reviewer agrees. This is not research verification.
