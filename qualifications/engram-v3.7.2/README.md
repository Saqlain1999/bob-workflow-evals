# Engram v3.7.2 qualification gate

This record supersedes the earlier Engram Alpha v0.11.0 source gate. Upstream
has moved to a different repository, Go implementation, command contract,
storage layout, release policy, and current security-support boundary. Reusing
the Alpha preview would therefore test an unsupported release with invalid
arguments. This gate maps the backend-neutral project-memory contract to the
current stable release without installing or executing Engram.

## Reviewed source

- Repository: <https://github.com/Gentleman-Programming/engram>
- Tag: `v3.7.2`
- Commit: `c6ba9e3c0e98ffa0d5591481d8670a575e7b70b0`
- Commit date: 14 November 2026 (UTC)
- Release published: 14 November 2026 (UTC)
- Licence: MIT; copyright remains with the upstream author
- Reviewed Linux asset: `engram_3.7.2_linux_amd64.tar.gz`
- Published asset digest: `sha256:8db9d5db1c1574b8b830aac4ffbe86c024014aed6b9a3f0406ac3361a152cdf0`

The release describes v3.7.2 as a packaging-only change over v3.7.1. The exact
v3.7.2 source still contains the v3.7.1 database-recovery, daemon-diagnostic,
project-ownership, hard-delete and MCP behavior reviewed here. The exact mapping
and source paths are in [`profile.json`](profile.json). No upstream source,
binary, script, prompt, skill, or documentation text is copied into this
repository.

## Decision

**Adapt after runtime evidence; do not adopt yet.** The current source is a
materially better candidate than Alpha v0.11.0: MCP runs directly over STDIO,
supports an explicit process project and tool allowlist, accepts an absolute
isolated data directory, provides project-owner assertions for update/delete,
and exposes hard deletion. It also documents backup/recovery and current stable
security support.

The full contract is not established:

- `expected_project` prevents an update or deletion from crossing project
  ownership, but it is not an expected-revision precondition for stale writers;
- source-hash freshness, explicit sanitized promotion, and honest outage
  fallback still need adapter behavior;
- recovery, project isolation, history/supersession, hostile-content handling,
  hard deletion and network silence still require disposable runtime evidence;
- upstream commit `82900dc5c61e534f4f3282ff19c211bbff3d5cd5`, merged after v3.7.2,
  corrects the released MCP's classification of unexpected project-resolution
  failures as `ambiguous_project`. On v3.7.2, a storage/session failure can
  therefore offer an inapplicable recovery token and project-choice guidance.
  Do not follow that guidance unless the error is independently shown to be
  genuine ambiguity; require a stable release containing the fix before
  accepting project-error recovery evidence;
- no Bob discovery, activation, tool approval, initialization-instruction
  review, or workflow-following has run.

## Safe preview

The preview helper renders, but does not write, a disabled project MCP entry and
the first read-only discovery call:

```sh
python3 scripts/preview_engram.py \
  --project /absolute/path/to/disposable-project \
  --binary /absolute/path/to/reviewed/engram
```

The output targets `<project>/.bob/mcp.json`, uses the absolute
`<project>/.engram-runtime` data directory through Bob's documented STDIO `env`
field, passes `mcp --project project-alpha` with an explicit minimum tool list,
sets update checks and cloud autosync off, starts disabled, and grants no
automatic tool approval. It never creates directories, changes Bob's global
configuration, downloads or runs Engram, or sends the discovery request.

Exact v3.7.2 source no longer accepts Alpha's `mcp --db` arguments or its
`brief` tool. Its first call is `mem_current_project`, and the trial must verify
the returned project/source before any write. The isolated data directory is a
source-backed input, not observed containment: the trial must still inspect all
created files, process/network activity, initialization instructions, project
boundaries, shutdown, deletion/index behavior, backup limits and removal.

Before a live Bob trial, independently verify downloaded bytes against the
published asset digest, inspect the generated project config, explicitly trust
only the disposable workspace, enable only this project server, and approve
tools individually. Stop if the source or digest differs, another data/config
location is touched, network activity occurs, stored instruction-like content
changes control flow, cross-project evidence leaks, a v3.7.2 project-resolution
failure offers ambiguity recovery without proven ambiguity, or a required
mutation cannot be demonstrated safely.

Removal for this preview is trivial because it writes nothing. Removal after a
future trial must cover the reviewed `.bob/mcp.json` entry, the isolated
`.engram-runtime` directory, any other observed state, indexes and backups. A
runtime removal procedure is intentionally not claimed before observation.
