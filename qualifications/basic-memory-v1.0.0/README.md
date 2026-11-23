# Basic Memory v1.0.0 qualification gate

This record maps the backend-neutral project-memory contract to the exact Basic
Memory v1.0.0 release without installing or executing it. It gives a later
disposable runtime comparison exact inputs, isolation boundaries, stop
conditions, and evidence gaps.

## Reviewed source

- Repository: <https://github.com/basicmachines-co/basic-memory>
- Tag: `v1.0.0`
- Commit: `c9bd187b83baba549d5cd16bacc180f8023d51c8`
- Commit date and release published: 29 October 2026 (UTC)
- Licence: AGPL-3.0-or-later; copyright remains with the upstream authors
- Python requirement: 3.12 or later
- Reviewed wheel: `basic_memory-1.0.0-py3-none-any.whl` (1,883,480 bytes)
- Published wheel digest: `sha256:a2d2c1589616c9599aec9edd6597d508028c5af88632312fc0990dcaccf02867`

The exact mapping and source references are in [`profile.json`](profile.json).
No upstream code, package, script, skill, prompt, or documentation text is
copied into this repository. The AGPL licence and its obligations need an
appropriate review before distribution, modification, or service deployment;
this source record is not legal advice or permission to redistribute.

The upstream MCP registry example invokes an unpinned package. This gate instead
requires the reviewed wheel by absolute path. Upstream `SECURITY.md` also still
lists `0.x.x` as supported even though v1.0.0 is released, so support status is
treated as an unresolved documentation inconsistency rather than inferred.

The pinned release also predates upstream commit
`3e8a519fa0ff406d98321af160080b74d8230c51` (13 November 2026), which corrected
`bm_project` listing so explicit local routing suppresses cloud discovery when
cloud credentials exist. Environment flags alone therefore do not prove that
v1.0.0 is local-only. Its first trial must start in a disposable process with no
Basic Memory cloud credentials or persisted login, observe network activity
before accepting the project list, and stop on any cloud discovery or request.

More importantly, exact v1.0.0 source blocks the project-separation claim. Its
`ContextService` has no confinement option, leaves the connected-entity project
filter empty for explicit relations, and hydrates relation targets with
`include_cross_project=true`. The pinned upstream test deliberately expects a
project-1 relation to expand into project 2 and a child relation. Upstream commit
[`506305b856967da1799f530502b6d9b7e6bd9610`](https://github.com/basicmachines-co/basic-memory/commit/506305b856967da1799f530502b6d9b7e6bd9610)
(22 November 2026) added optional confinement after a cloud security audit, but
kept traversal enabled by default for local use. That unreleased change is not
evidence for v1.0.0 and does not expose a reviewed confinement control for this
local STDIO trial.

## Decision

**Defer pending project confinement; do not execute or adopt v1.0.0 yet.** Exact
v1.0.0 source has
useful controls: named project routing, project-root validation, local STDIO,
checksum-guarded edits and deletes, and project deletion disabled by default.
Those remain useful candidates for stale-writer refusal and lifecycle testing,
but project arguments and roots do not confine graph-context traversal.

The bounded next slice is either a stable reviewed release that exposes
project confinement on the local STDIO MCP path, or a reviewed wrapper that
blocks `build_context` and filters every cross-project metadata/content path.
Its acceptance fixture must create an explicit project-alpha to project-beta
relation whose alpha-authored label differs from the uniquely named beta target,
plus a beta child link. A context request from alpha may retain that author-owned
label, but must return no backend-hydrated beta title, path, external ID, child
graph link, or body. Missing confinement or any disclosure is a stop, not a
partial qualification.

They do not establish the contract:

- package dependencies and optional model/cache downloads have not been
  resolved or observed;
- supersession history, source freshness, sanitized promotion, and outage
  fallback still need a bounded adapter;
- project isolation is blocked by source; atomic recovery, hostile-content
  handling, checksum races,
  and direct/indexed deletion still need disposable runtime evidence;
- local file deletion is irreversible, cloud deletion has different backup
  semantics, and the first trial deliberately excludes cloud mode;
- no Bob discovery, activation, approval, or workflow-following has run.

## Safe preview

The preview helper renders, but does not write, an isolated Basic Memory config,
a disabled project MCP entry, and the first read-only project-list call:

```sh
python3 scripts/preview_basic_memory.py \
  --project /absolute/path/to/disposable-project \
  --uvx /absolute/path/to/reviewed/uvx \
  --wheel /absolute/path/to/basic_memory-1.0.0-py3-none-any.whl
```

The output targets `<project>/.bob/mcp.json`, constrains Basic Memory to the
named local project, moves its configuration/cache under
`<project>/.basic-memory-state`, disables cloud routing, promos, Logfire export,
auto-update, project deletion, and all Bob auto-approval, and starts disabled.
It never creates a directory, writes either config, downloads or imports the
wheel, starts `uvx`, or sends the tool request.

The preview remains useful for configuration review, but it is not permission
to start v1.0.0 while the project-separation gate is blocked. After a confined
artifact or wrapper is separately reviewed, the text-search preview still does
not prove v1.0.0 avoids model or dependency downloads. Before execution, verify the
wheel digest independently, review and write both rendered files only in the
disposable project, remove Basic Memory cloud credentials and persisted login
state from the disposable process, explicitly trust that folder if Bob folder
trust is active, enable the one server manually, retain individual tool
approvals, and observe network activity before accepting `bm_project` output.
Stop if the release changes, cloud discovery or a network request occurs, a
global or cloud setting is required, confinement is absent, any backend-hydrated
other-project title/path/external ID/child graph link/body is visible, a
stale checksum succeeds, or the repository-evidence fallback is ambiguous.

Removal for this preview is trivial because it writes nothing. A future trial
must document removal of the project MCP entry, isolated config/database/logs,
downloaded dependency and model caches, indexes and any retained backups. That
procedure is intentionally not claimed before the lifecycle is observed.
