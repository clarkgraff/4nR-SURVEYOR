# Increment D1: bounded source acquisition + discipline separation

**Implemented:** operator-authorised HTTPS text/HTML/JSON retrieval, finite size limits, content SHA-256 archive & append-only provenance events; explicit rejection of unapproved hosts, redirects and unsupported media. Tests mock network; no claim of live source retrieval is made.

**Security:** only permit deliberately authorised public hostnames. Network egress filtering and a DNS-pinning transport are still required before deploying an automatic acquisition worker; DNS prechecks alone cannot eliminate DNS rebinding. Do not pass model-generated URLs to acquisition without human approval.

**Evidence:** source downloads are labelled `retrieved_not_reviewed`. No automatic truth certification. This increment does not implement claim extraction, source corroboration, scholarly search connectors or research licences.

**Developer tests:** `python -m unittest discover -s tests -v`. Expected 23 tests after sync. The normal research CLI remains available. Source acquisition is a Python module only (no CLI/network API yet).

**Delegation:** specialist instructions require discipline-limited reporting; avoid repeating the entire mixed-domain answer in every child. No cross-child synthesis or automatic task decomposition implemented yet.

**Pending:** source parsing & provenance mapping, bounded claim extraction, reviewer workflow, local archive searching and source-backed research prompts.
