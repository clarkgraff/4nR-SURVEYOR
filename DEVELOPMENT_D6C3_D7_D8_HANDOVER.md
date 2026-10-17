# Consolidated development handover — D6C-3, D7 and D8

These increments operate on the existing `development/parent-runtime-increment-a` branch. No FWaS email, Azure or NERDS dependencies were added.

## D6C-3: Investigation handoff
A `decide ... investigate_further` command now records the user disposition and creates a durable, queued research handoff in SQLite. The handoff retains the presentation identity, original source URL and user's question. It does not approve source acquisition.

Use `run-handoff JOB_ID` to execute the **already queued** research job. The research pipeline creates its own linked sub-job, and an expanded presentation with unverified claims. Optional `--reviewer CHAKOTAY` runs D5's limited model assessments. **Video contents are not automatically downloaded or transcribed.** The original YouTube record is only metadata and a reference URL; the follow-up must not be described as evidence-backed unless actual approved sources are supplied in a future extension.

Example:
```powershell
python -m surveyor decide "surveyor-archive\presentations\ACTUAL_ID.json" 4 investigate_further --operator "Operator" --reason "Review original UNESCO documentation" --archive surveyor-archive
# The returned handoff.job_id is the next command's JOB_ID:
python -m surveyor run-handoff JOB_ID --archive surveyor-archive
```

Prior user decisions recorded before this code update are not automatically backfilled. For an existing recorded `investigate_further` decision, use:
```powershell
python -m surveyor handoff "surveyor-archive\presentations\ACTUAL_ID.json" 4 --reason "Review original UNESCO documentation" --archive surveyor-archive
```

## D7: Shared knowledge catalogue
A separate local SQLite catalogue accepts **only a discovery candidate with the latest recorded decision of `approve`**. Catalogue entries retain the suite, source URL, operator decision, presentation ID and source index. They are always labelled `curated_candidate_unverified`; human workflow approval does not establish factual accuracy.

```powershell
python -m surveyor knowledge-add "surveyor-archive\presentations\ACTUAL_ID.json" 4 --archive surveyor-archive
python -m surveyor knowledge-search "Morna"
```
D7 does not implement validated claim promotion, semantic search, trained-model updates, autonomous learning, or cross-suite knowledge synthesis.

## D8: Local user interface (initial functional prototype)
```powershell
python -m surveyor gui --archive surveyor-archive
```
Tkinter is part of the supported Python desktop runtime if installed with Tcl/Tk. It displays archived presentations, links, basic metadata and user-decision controls. It can queue follow-up jobs and curate approved discovery candidates. It **does not yet** run a full new search, render multimedia, execute queued research inside the UI, or display full vetted narrative reports. This is a first local desktop interface, not the complete end-user application described in the governing scope.

## GMKtec validation
```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
$env:PYTHONPATH="src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compile failed" }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
```

Expected suite size: **85 tests** (previous 78 + 4 handoff + 3 knowledge). Unit tests exercise the GUI's domain operations but do not attempt to open a desktop window; manually verify `python -m surveyor gui` after tests pass.

## Security and future work
The D8 local GUI is not an identity platform. User/operator text is a provisional local label, not Entra-authenticated identity. Audit JSONL integrity detects modifications under single-process assumptions, not concurrent writes or adversarial file replacement. Do not use externally shared archive directories for this prototype. Do not assume YouTube API metadata validates recording content. Future development must add supported acquisition for independent scholarly evidence, comprehensive discovery-to-vetting automation, reviewed claim promotion and full graphical research interaction.
