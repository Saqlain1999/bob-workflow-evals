# Backend qualification records

These records turn the backend-neutral
[`bob-project-memory-v1`](../fixtures/bob-project-memory/README.md) contract into
reviewable backend-specific gates. A record is not an installer, endorsement,
live Bob result, or production-readiness claim.

Each backend record must pin the reviewed source and release, state its licence,
map every contract behaviour to evidence or a named gap, and keep installation
and execution outside this repository's offline test suite. Preview helpers may
render configuration, but must not write Bob settings, start a server, download
a binary, or call a model.

| Record | Decision | Evidence boundary |
| --- | --- | --- |
| [`engram-v3.7.2`](engram-v3.7.2/README.md) | Adapt only after runtime qualification | Current stable source-reviewed profile and non-mutating Bob project-config preview; supersedes the unsupported Alpha v0.11.0 gate; no Engram or Bob execution |
