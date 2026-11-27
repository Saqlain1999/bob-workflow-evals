# Result records

No participant run or aggregate benchmark result is included yet.

Copy `result-template.json` for each real run. Keep unknown values as `null` and
retain `not_run` or `not_assessed` until evidence exists. The template itself is
not a result.

The template defaults to Tiny Ledger. For Parcel Resume, set `task_id` to
`parcel-resume-v1`, update `procedure.exact_prompt_file` to
`tasks/parcel-resume/AGENT_PROMPT.md`, and identify the checkpoint origin as
`constructed_by_preparation_helper`. Use `recovery` to link the real historical
check, preparation record and file fingerprints. Keep checkpoint usefulness
and observed stale-evidence rechecking `not_assessed` until a human can support
those findings. A helper pass alone is not that observation.

The offline helper writes a separate evidence report for baseline and candidate
checks. Reference those reports from the participant record; do not confuse
their test duration with the agent's task duration.

Generated local workspaces and reports can live under the git-ignored `runs/`
directory. Before contributing a record, remove credentials, confidential code,
private paths, and unrelated conversation content. Explain redactions and
include enough evidence to assess the specific claim. Review the participant's
code and test changes before recording manual acceptance.

Memory backend runtime evidence uses the separate
[`memory-runtime-trial-template.json`](memory-runtime-trial-template.json) and
the [runtime protocol](../qualifications/memory-runtime-trial-v1/README.md).
That template is not participant evidence and defaults to an unauthorized,
unexecuted Engram v3.7.2 result. Rebind all profile, qualification, commit and
asset-digest fields together to inspect Basic Memory v1.0.0 as `not_run`; its
source gate blocks every executed decision until project confinement is
reviewed. Superseded profiles are rejected. Validate a completed copy outside
the candidate workspace; the validator confirms claim consistency, rejects
duplicate JSON object names, and rejects fields outside the reviewed schema
rather than ignoring typoed or extra claims. A `not_run` record cannot carry
run, observation-time, host, client-name/version, trust, side-effect, cleanup,
or behavior observations. Every executed record must name a distinct
non-secret host identifier, a valid second-precision RFC 3339 UTC observation
time at or after the pinned artifact's recorded release, and the observed
client implementation and version. A generic client category is not a
reproducible client identity. The
source section must also record the lowercase SHA-256 actually observed from
the artifact and a non-secret evidence reference for that verification; the
observed digest must equal the reviewed profile digest. A Boolean verification
claim alone is rejected. The validator does not run or qualify a backend. The
current schema also requires
lifecycle hooks to be disabled so a permission hook cannot substitute for a
manual approval. Cleanup outcomes are
valid only when `cleanup.attempted=true`; an unattempted cleanup cannot claim
that processes stopped, files were removed, or machine state was cleaned.
