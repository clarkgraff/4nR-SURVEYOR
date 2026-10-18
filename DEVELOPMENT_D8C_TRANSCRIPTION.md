# D8C initial implementation — local transcription & subtitle foundations

Committed on `development/parent-runtime-increment-a`; requires GMKtec testing.

## Implemented
- An optional **offline faster-whisper** speech-to-text adapter. It requires a locally installed model directory and does not automatically fetch models.
- Media integrity recheck, FFmpeg audio derivative generation and timecoded transcription records stored in the SURVEYOR archive.
- Separate transcript and translation record schemas. Translation execution, speaker diarisation, lyrics-specialised recognition, transcript correction and GUI transcript display **are not yet implemented**.
- SRT and WebVTT subtitle generation, with source-relative timecodes.
- Automated tests for the format and validation logic.

## Run validation first
```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Git pull failed" }
$env:PYTHONPATH = "src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compilation failed" }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Automated tests failed" }
```
Expected count **96 tests** (prior 90 + six new). Tests use no hosted model and do not demonstrate live transcription.

## Optional local speech test
Only after selecting and installing an offline faster-whisper-compatible model, on the same Python interpreter:
```powershell
python -m pip install faster-whisper
python -m surveyor transcribe MEDIA_SHA256 --model-path "C:\PATH\TO\EXTRACTED_LOCAL_WHISPER_MODEL" --archive surveyor-archive
```
Use an actual, consented speech recording, **not** the prior 440 Hz sine-wave fixture. Copy the resulting `transcript_path` and run:
```powershell
python -m surveyor subtitles "PATH\TO\TRANSCRIPT.json" --format srt --output "transcript.srt"
python -m surveyor subtitles "PATH\TO\TRANSCRIPT.json" --format vtt --output "transcript.vtt"
```
The model's accuracy, performance, language coverage and hardware backend on GMKtec remain untested. The adapter defaults to CPU int8; selecting another execution backend requires separate benchmark evidence. Install an appropriate locally available model separately; models are not bundled.

## Future increment
Implement local translation inference with a distinct provenance record, transcript correction revisions, source-relative translation segment alignment, robust long-duration media handling, cancellation & progress display, and GUI integration. Preserve original media, raw machine result and independently authored human corrections.
