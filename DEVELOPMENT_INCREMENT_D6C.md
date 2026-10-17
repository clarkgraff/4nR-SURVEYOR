# D6C — Research presentation and operator disposition (first implementation)

The D6C user presentation stage is now callable locally without FWaS email, Azure or NERDS.

## Present archived discovery to a user
Supply the exact existing discovery report file, e.g. the one returned from the live YouTube test:
```powershell
python -m surveyor present "surveyor-archive\discovery\4ae5a9c83b614133b7fb9ffd92b62461.json" --archive surveyor-archive
```
This prints linked sources and persists a separate `surveyor.presentation.v0` JSON snapshot under `surveyor-archive/presentations`. The output includes `presentation_path`; copy that path for the next command.

If a `surveyor.pipeline.v0` report has already been saved as JSON, the command supports `--pipeline-result path-to-file.json` to include separate, explicitly unverified claim drafts and vetting assessments. Discovery alone **does not** fetch YouTube video contents or generate claims.

## Record a decision
```powershell
python -m surveyor decide "surveyor-archive\presentations\ACTUAL_PRESENTATION_ID.json" 1 investigate_further --operator "Clark" --reason "Verify source and performer identity" --archive surveyor-archive
```
Replace the placeholder with the path shown in `presentation_path`. Supported actions: `approve`, `investigate_further`, `flag_correct`, `save_for_later`. Decisions append to `presentation-decisions.jsonl` via a hash-linked audit record.

**Approval is only a workflow disposition**; no candidate is automatically declared factually verified or suitable for vessel navigation. The user-facing interface is currently PowerShell JSON, not a graphical application. Automated user assignment, sending mail, autonomous discovery-to-investigation handoff, automatically applying user corrections, and human-reviewed promotion to a knowledge catalogue remain future work.

## Tests
```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Pull failed" }
$env:PYTHONPATH = "src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compile failed" }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
```
Expected total **78 tests** (72 previous + 6 presentation tests). The GMKtec has not yet run this increment.
