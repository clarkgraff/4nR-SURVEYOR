# Increment D4 — PowerShell research pipeline interface

This adds `python -m surveyor pipeline` to the existing CLI.

The command routes to D3's `run_pipeline`, records a persistent job and prints structured output. A caller may provide a primary specialist, a different reviewer, and an explicitly approved source URL/hostname pair. Network acquisition is refused unless `--allow-download` is supplied.

## Offline-model test (no sources, not evidence-backed)

```powershell
cd "$HOME\4nR-SURVEYOR"
$env:PYTHONPATH = "src"
$env:SURVEYOR_MODEL = "Qwen3-30B-A3B-GGUF"
python -m surveyor pipeline EMERSON "Return one preliminary claim about morna." --scope "Test only" --archive "surveyor-archive"
```

## Explicitly approved source example

This illustrates the CLI syntax. Do not automatically execute against an unreviewed URL.

```powershell
python -m surveyor pipeline EMERSON "Investigate morna with supplied source evidence" --scope "Pilot with approved source" --source "https://example.org/approved-document" --approve-host "example.org" --allow-download --reviewer CHAKOTAY
```

The current acquisition adapter accepts only HTTPS text/plain, text/html or application/json with a 2 MB maximum; blocks redirects and unapproved hostnames. Network egress enforcement/DNS-pinning is still a deployment requirement. Only use approved public hosts and review source terms.

## Limitations

- The pipeline presently requires clean structured JSON from Qwen3; malformed or wrapped output fails the job and is recorded.
- The peer assessment is a model proposal, never verification.
- Source matching is lexical and may be misleading.
- No unrestricted external web discovery, autonomous download, semantic evidence entailment, human approval UI, or NERDS integration.
- The first stage of the live D4 test should be source-free to validate the model's structured output before manually approved source acquisition.

## Verification

Five original D3 tests and four additional CLI tests. Full expected suite: **42** tests, pending GMKtec execution. Existing research DB is reused unless `--db` is changed.
