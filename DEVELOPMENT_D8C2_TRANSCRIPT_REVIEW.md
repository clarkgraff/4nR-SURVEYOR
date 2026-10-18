# D8C-2 transcript review checkpoint

Development branch: `development/parent-runtime-increment-a`.

Added a local **Review Transcript** window for archived SURVEYOR transcript JSON. It shows segment text and timecodes, allows each segment's text to be corrected, and persists a **new immutable revision** with operator, reason, parent file hash, original recording identity and every replacement. The original machine transcription remains unchanged. Subtitle generation supports corrected revisions through the existing `subtitles()` function.

This first editing window does **not** provide synchronised audio playback yet. Translation inference, diarisation, specialised lyrics recognition and a dedicated SURVEYOR virtual environment also remain future work. Corrections are human-attributed, not automatically verified research facts.

## GMKtec verification
```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
$env:PYTHONPATH="src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compile failed" }
python -m unittest discover -s tests -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed" }
python -m surveyor gui --archive surveyor-archive
```
Expected **99 passing tests** (previous 96 plus three revision tests). GUI acceptance: select `Review Transcript`, open the archived Bobby recording transcript, select its first segment, replace `Lidafor` with `Lita Ford` while preserving the other words, click `Stage correction`, supply a substantive reason, click `Save revision`. Verify the new path appears under `surveyor-archive/language/revisions` and the original `surveyor-archive/language/transcripts` record is unmodified.

This checkpoint is code committed, **not independently run on GMKtec yet**.
