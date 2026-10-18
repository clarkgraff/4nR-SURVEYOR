# D8A / D8B — Media acquisition foundation, archive & audio derivatives

Branch: `development/parent-runtime-increment-a`. NERDS and Resolve are unchanged.

## Current functionality
- D8A: user-initiated **local media import**, original-byte preservation, SHA-256 content identification, duplicate detection, source attribution, permission basis, recorded operator, acquired time, and archive integrity checking.
- D8B: `ffprobe` source stream/container metadata and `ffmpeg` 16 kHz mono PCM WAV **derived** audio, retaining the original file. The derivative includes its own SHA-256 and a link to the original.
- GUI: `Import Media` launches a native file picker. The operator and permission basis are explicitly required (the current prototype uses the existing operator and rationale fields).

## Explicit boundaries
- No general-purpose video ripper or social-media site adapter is provided yet.
- URL provenance is only an optional *record of origin* in local imports, **not permission to retrieve it**.
- The earlier HTML/JSON acquisition service remains separate, with its existing bounds.
- No DRM circumvention, no background media downloads, no automatic online provider access.
- ffprobe/ffmpeg binaries must be locally installed and available on PATH for D8B.
- Audio-to-text, translation, diarisation, analysis and provider-specific authorised downloads follow separately.
- No claim of factual verification arises from a successful download, import or technical inspection.
- Future plugin host and Resolve exchange design is specified in `FUTURE_PLUGIN_ARCHITECTURE.md`; **neither is implemented**.

## On-GMKtec validation
```powershell
cd "$HOME\4nR-SURVEYOR"
git pull --ff-only
if ($LASTEXITCODE -ne 0) { throw "Pull failed" }
$env:PYTHONPATH="src"
python -m compileall -q src tests
if ($LASTEXITCODE -ne 0) { throw "Compile failure" }
python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Unit test failure" }
python -m surveyor gui --archive surveyor-archive
```
Expected suite: 90 tests (previous 85 plus five media tests); pending GMKtec confirmation.

Manual media test: put a permitted short WAV audio recording in a local folder, then:
```powershell
python -m surveyor media-import "C:\PATH\TO\YOUR\OWNED.wav" --operator "Clark" --permission "Owned recording" --archive surveyor-archive
```
Copy `sha256_hex` returned by the import, then test:
```powershell
ffprobe -version
ffmpeg -version
python -m surveyor media-probe YOUR_SHA256 --archive surveyor-archive
python -m surveyor media-audio YOUR_SHA256 --archive surveyor-archive
```
A fake unit-test WAV is *not* a valid fixture for real FFmpeg and must not be used for manual media validation. Use a real permitted recording.

## Acceptance status
Committed for external host validation. The unit tests and FFmpeg integration have not yet been run on the GMKtec. GUI imports require manual acceptance.
