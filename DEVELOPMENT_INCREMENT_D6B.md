# D6B — Initial live provider: YouTube

Implemented an official YouTube Data API v3 search connector for videos and channels, mapped to the existing `DiscoveryHit` / `surveyor.discovery.v0` format.

**Bandcamp:** Bandcamp's published developer API does not expose a general public artist-search method. No undocumented endpoint, scraping bypass or fictitious connector has been added. Bandcamp remains a manually curated source via the D6A manifest while a supported discovery route is evaluated.

## GMKtec validation
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
Expected automated-test count: **72** (65 prior + seven YouTube tests).

## Live authorised test (requires user-provided key)

Register a Google Cloud project with YouTube Data API v3 enabled and an appropriately restricted API key. In PowerShell set the key for the current process only:
```powershell
$env:SURVEYOR_YOUTUBE_API_KEY = Read-Host "YouTube Data API key"
python -m surveyor discover EMERSON "Cape Verde morna traditional musicians" --provider youtube --live --archive surveyor-archive --limit 10
Remove-Item Env:SURVEYOR_YOUTUBE_API_KEY
```

Avoid exposing API keys in screenshots/logs. Search requests use bounded response sizes, no video downloads and no automatic full-content acquisition.

**Limitations:** official YouTube API access and live search have not been validated on the user's GMKtec. Results are metadata-only, `discovery_only`, not independently reviewed. Real provider availability depends on credentials, quota, network and terms. The query credential is sent to Google's endpoint and is not stored in SURVEYOR output. Further hardening is required before unattended deployment, particularly credential redaction from HTTP exception messages and managed key restrictions. No automatic cross-provider corroboration, Bandcamp public API, or FWaS email/Entra dependency.
