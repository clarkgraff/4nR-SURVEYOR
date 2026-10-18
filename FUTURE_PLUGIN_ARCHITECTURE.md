# SURVEYOR future plugin architecture — design reservation only

Status: **specified, not implemented or tested**. The plugin-host implementation and DaVinci Resolve adapter are intentionally deferred.

## Native extension contract (future)
- Plugin identity, vendor, semantic API version, declared capabilities, signed/trusted installation origin and compatibility requirements.
- Capabilities: media import, technical analysis, transcription, translation, subtitle export, controlled evidence lookups, contribution proposals.
- Permission model: no implicit file reads, downloads, external connections or knowledge promotions; user-scoped access to a designated archive.
- Lifecycle: discover -> check compatibility -> consent -> activate -> execute -> revoke -> unload, with bounded execution and structured errors.
- Immutable source identity: SHA-256; timecoded annotations and derivative relationships reference the original.
- Bidirectional knowledge exchange: versioned read and proposed-write contracts, causal linkage to source IDs and timecodes, operator attribution, human approval, full audit history. A plugin's proposed corrections never silently overwrite research evidence.
- Future Blackmagic Design DaVinci Resolve integration: supported Resolve scripting / workflow-integration adapter exchanging timecoded transcripts, translations and production metadata, without requiring Resolve to run SURVEYOR.
- Security and interoperability tests will be designed when host implementation is authorised in a later increment. No binary compatibility claim is made.

## Implemented now
D8A media import and D8B FFmpeg processing are native Python services; they **do not** use or require a plugin host.
