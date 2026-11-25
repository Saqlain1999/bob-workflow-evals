# Project-memory runtime trial protocol

This protocol makes later project-memory trials comparable and
fail-closed. It binds a result to one reviewed backend profile, the exact
published asset digest, the ten `bob-project-memory-v1` behaviours, observed
side effects, cleanup, and explicit evidence limits.

The allowed Engram profile is the current reviewed v3.7.2 source gate. The
superseded Alpha v0.11.0 profile is intentionally rejected. Basic Memory v1.0.0
remains an allowed `not_run` binding so its exact source and asset identity can
be reviewed with the same evidence shape. It is blocked before execution because
its source gate records unconfined cross-project context traversal. A later
confined release or wrapper needs a reviewed profile and the named A-to-B
disclosure fixture before execution can be enabled here.

It is an evidence protocol, not permission to run software. The template keeps
execution unauthorized and every behaviour `not_run`. The validator reads JSON
only: it does not download an asset, write Bob settings, start a process, call a
model, or contact a service.

A `not_run` record must remain wholly unobserved: it cannot name a run ID,
observation time, host identifier, host operating system or architecture,
client version, explicit workspace-trust
decision, verified asset, side effect, cleanup action, or behavior evidence.
Record those facts only after separately authorized execution actually begins.

## Before an authorized trial

The current executable profile is Engram v3.7.2 only. Do not begin the Basic
Memory v1.0.0 steps below; they remain documented for a future confined profile,
not as execution permission.

1. Use a disposable project containing only the constructed public fixture.
2. Obtain separate authorization to download or execute the reviewed third-party
   artifact.
3. Independently verify the artifact digest against the selected profile.
   Record the lowercase SHA-256 actually observed from the downloaded bytes and
   a non-secret reference to the verification evidence. Do not copy the expected
   value into the observed field without performing and retaining that check.
4. Review the disabled project-only STDIO preview and retain manual tool
   approvals. Disable global, workspace, plugin, and policy lifecycle hooks;
   permission hooks can resolve approvals without user interaction, while other
   hooks can inject context, change inputs, execute commands, or call HTTPS
   endpoints. Stop if an enforced hook cannot be disabled. If Bob is used, use
   an interactive IDE or Shell session and record the client mode, version, and
   explicit folder-trust decision. Bob
   Shell non-interactive sessions are outside this first protocol because
   [their tools are pre-approved](https://bob.ibm.com/docs/shell/getting-started/start-bobshell-non-interactive),
   which conflicts with the manual-approval safeguard.
5. Copy [`memory-runtime-trial-template.json`](../../results/memory-runtime-trial-template.json)
   outside the candidate workspace and fill it from observed evidence. Use a
   distinct non-secret, pseudonymous host identifier and the actual observation
   time as a second-precision RFC 3339 UTC value such as
   `2026-11-24T08:00:00Z`; do not put a personal machine name or secret in the
   host field.

Record process, file, network and model-download effects even when the observed
answer is “none”; include how each observation was made. Record MCP server
instructions returned during initialization separately because current Bob IDE
can forward them into the system prompt. Exercise the same ten behaviours for
each backend. Keep repository evidence as the outage fallback.
Stop on a digest mismatch, global-setting or lifecycle-hook requirement,
cross-project disclosure, instruction-like stored content changing control
flow, a stale write being accepted, dishonest outage success, or incomplete
deletion.

Validate a record from the repository root:

```sh
python3 scripts/validate_memory_trial.py path/to/trial.json
```

Exit `0` means the record is internally consistent with its decision. It does
not mean the backend qualified: inspect the emitted decision. Exit `2` means
the evidence record is invalid or overclaims its observations. The validator
rejects repeated JSON object names at any depth rather than silently selecting
one of two conflicting decisions, identities, safeguards, or observations. It
also rejects missing, misspelled, or unrecognized fields at every level of the
runtime record; extending the evidence shape requires an explicit schema change
rather than an unchecked extra claim.

`qualified` is intentionally narrow. It requires all ten behaviours to pass,
successful cleanup, and complete side-effect evidence. It never means production
ready. Every executed IBM Bob record—including a blocked or incomplete
trial—requires an observed interactive client mode and version, explicit
workspace trust, and `live_bob_observed=true`. This records where the evidence
came from; it does not turn a blocked or incomplete result into backend
qualification. Direct MCP records must instead mark workspace trust as not
applicable. Every executed record also names its operating system,
architecture, a distinct host identifier, and a valid UTC observation time.
Those fields bind evidence to an event and environment; the validator does not
attest that their contents are truthful. It likewise requires an observed
artifact SHA-256 equal to the pinned digest plus a verification-evidence
reference, but cannot attest that the referenced command or bytes are genuine.
Backup erasure, privacy/licence
compliance, durable multi-process safety and production readiness remain
separate gates.

Cleanup evidence must also remain internally consistent for blocked and
incomplete trials. A record with `cleanup.attempted=false` cannot claim that
processes stopped, project files were removed, or machine state was removed or
absent. Set `attempted=true`, add notes, and record each observed outcome when a
cleanup attempt actually occurs; otherwise leave every cleanup outcome false.
