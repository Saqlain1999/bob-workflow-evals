# Memory boundaries v1 — qualification scaffold, not a memory integration

Status: an original, offline trace-contract checker and synthetic controls.
No Engram, Basic Memory, Honcho, Bob client, model, or memory service runs here.
A passing trace is **not** an authenticated backend observation or proof of
persistent recall, project authorization, deletion, or prompt-injection resistance.

This independent slice starts from `main`; it does not depend on the reminder
PR stack and does not change its evaluator, fixtures, workflow, or installer.
It advances [the shared product roadmap](https://github.com/Saqlain1999/bob-workflow-kit/issues/3).

## Run the controls

From the repository root with Python 3.10+ (standard library only):

```sh
python -B -W error::ResourceWarning -m unittest discover -s tests -p test_memory_trace.py -v
python -B scripts/check_memory_trace.py fixtures/memory-boundaries/synthetic-control.json
```

The first command exercises the checker, including deliberately faulty traces.
The second must report `trace_contract_passed`, ten cases, and an explicit
execution-provenance limitation. The control file is hand-authored synthetic
evidence, not a backend result. No backend is selected by this success.

For a future reviewed adapter, save its normalized **public-fixture** observation
outside the fixture and run `python -B scripts/check_memory_trace.py PATH.json`.
Exit codes: 0 = submitted finite trace passes; 1 = contract failure; 2 = unreadable,
malformed, duplicate-key, nonfinite-number, or oversized JSON. Reads are capped at
64 KiB; diagnostics contain at most 20 error codes, never supplied memory text.
Input files are read-only. There is no network, shell evaluation, auto-install,
configuration write, background process, or model call.

## Finite contract

`contract.json` is trusted repository input. It defines ten original synthetic
records and ten test queries; `synthetic-control.json` shows the result format.
All private-looking strings are invented canaries, not actual confidential data.
Only the expected records may appear in each final brief. Ordering is irrelevant;
duplicates, omitted cases, unknown fields/records, and changed provenance fail.

| Case | Required observation |
| --- | --- |
| Fresh session | The active alpha retry decision is present. |
| Project isolation | No beta project note appears in alpha's brief. |
| Explicit sharing | Beta receives the approved generalized lesson, not alpha's raw note. |
| Supersession | Only decision-2 appears as current, not retired decision-1. |
| Stale verification | The source-v1 pass is labelled historical when current source is source-v2. |
| Deleted record | The deleted record is absent from the selected brief. |
| Poisoned record | A quarantined instruction-bearing note is absent. |
| Trust domain | A same-named project in another trust domain cannot supply the brief. |
| Task isolation | A different task's working note is absent. |
| Backend outage | `unavailable` is explicit; an empty `ok` result is rejected. |

Every case labels memory `untrusted_data`, not system authority. Every expected
record retains its exact content, source, and revision. The checker detects
particular contract violations in submitted JSON; it does not itself implement
routing, permissions, quarantine, sharing, retrieval, redaction, or deletion.
Relabelling arbitrary input is not an authorization mechanism.

## Same qualification for both shortlisted backends

The user agreed on 25 October 2026 to an optional project/cross-project memory
capability: adopt an existing store rather than build a new database. Keep task
notes, project knowledge, explicitly shared sanitized lessons, and user/team
preferences distinct. Keep separate trust domains separate at the process,
credential, storage, or server-enforced authorization boundary, not merely in a
prompt or query filter. Never ingest private employer/client code or credentials.

Candidate decisions, inspected 25 October 2026 (not installation advice):

- **Engram Alpha: qualify, do not adopt by default yet.** Reviewed revision
  [`996099afbd68366ed4671fa0cac11cd8fa929654`](https://github.com/techtheist/engram/tree/996099afbd68366ed4671fa0cac11cd8fa929654),
  commit dated 18 October. Its [getting-started document](https://github.com/techtheist/engram/blob/996099afbd68366ed4671fa0cac11cd8fa929654/docs/getting-started.md)
  describes Bob-specific project MCP and SessionStart wiring. Its
  [security document](https://github.com/techtheist/engram/blob/996099afbd68366ed4671fa0cac11cd8fa929654/SECURITY.md)
  explicitly describes a single-user local API without authentication, redaction
  gaps for tags/code references/edge notes, freed-page deletion residue, and
  model downloads without pinned checksums. Treat these as upstream disclosures,
  not independently reproduced incidents. The [licence is MIT](https://github.com/techtheist/engram/blob/996099afbd68366ed4671fa0cac11cd8fa929654/LICENSE).
- **Basic Memory: qualify as the inspectable baseline.** Reviewed revision
  [`4bcfc0665744960f514a0ff61f4f432aa8cfe54f`](https://github.com/basicmachines-co/basic-memory/tree/4bcfc0665744960f514a0ff61f4f432aa8cfe54f),
  commit dated 24 October. Its [project documentation](https://docs.basicmemory.com/concepts/projects-and-folders)
  describes separate knowledge bases and explicit multi-project search. Its
  [pinned edit manual](https://github.com/basicmachines-co/basic-memory/blob/4bcfc0665744960f514a0ff61f4f432aa8cfe54f/src/basic_memory/man/man3/bm-edit%283%29.md)
  documents an optional `expected_checksum` revision guard. The reviewed
  [licence is AGPL-3.0](https://github.com/basicmachines-co/basic-memory/blob/4bcfc0665744960f514a0ff61f4f432aa8cfe54f/LICENSE),
  not MIT; do not copy its implementation into this MIT repository or bundle it
  without a separate licence/distribution review. No code is copied here. A future
  optional external integration must qualify its exact tool surface and local
  configuration; public tool names and pinned manuals can differ across versions.
- **Honcho: retain as an optional later candidate**, not a selected implementation.
  No new source/runtime qualification of Honcho is claimed by this slice.
- **Native project notes: retain as the comparison condition**, not automatically
  replace them. Additional storage must demonstrate a useful recall outcome.

The two commit dates above are Git commit dates, not inferred release dates.
External web documentation is inspection-dated and mutable. Neither backend,
its installer, binary, model weights, or dependencies was executed or downloaded.
No performance comparison or winner is claimed.

## Bob-specific gates

IBM's [IDE hooks](https://bob.ibm.com/docs/ide/configuration/lifecycle-hooks) and
[Shell hooks](https://bob.ibm.com/docs/shell/configuration/lifecycle-hooks),
inspected 25 October, document SessionStart context injection. SessionStart is
**non-blocking**: an exit code cannot make it an authorization gate. Shell skips
workspace hooks in untrusted folders. A future adapter must record missing hooks
and unavailable memory honestly, preserve existing settings, and qualify IDE and
Shell separately. MCP connectivity alone does not prove capture or recall.

Start with manual opt-in retrieval in disposable public fixtures. Only after
source/dependency review and observed backend checks should optional hooks be
considered. Do not run upstream setup against an active Bob home; do not install
multiple memory systems, introduce an always-on daemon, or expand the runner.
Keep capture curated and off by default, with explicit approval for cross-project
promotion. A model statement is not automatically a verified project fact.

## Required next implementation and evidence

1. Review the pinned runtime, dependencies, local settings, storage and removal
   paths. Implement a small optional adapter for each shortlisted backend using
   the same fixture, not two new storage engines. Record actual tool names and
   configurations; do not translate mutable documentation into assumed support.
2. In disposable isolated homes, seed the public records and record backend output
   before filtering. Reconnect/restart before the fresh-session query. Explicitly
   apply supersession/deletion and simulate an outage. Preserve raw evidence and
   normalization rules; do not cherry-pick correct hits or fabricate provenance.
3. Check leakage at BOTH raw retrieval and delivered-brief boundaries. A final
   brief pass alone does not establish server isolation. Exercise hostile note
   text outside this finite canary. Prove that unsupported capabilities remain
   unavailable rather than silently passing.
4. Add observed optimistic-conflict/two-writer, interrupted-write, export/removal,
   index/deletion/backup-retention, and configuration-preservation tests. These are
   **not tested by this trace checker**. Compare against native notes with the
   same questions and record failed runs, interventions and unknown measurements.
5. Keep live Bob discovery, new-session recall, skill use and approval-denial
   behavior as separately authorized client/version-specific observations. No
   backend or helper pass upgrades a live-client maturity label.

A reviewed backend may be adopted only after these relevant gates have evidence.
Keep the reminder remediation/re-review work progressing independently. This
scaffold is the first memory qualification slice, not a completed memory system.
