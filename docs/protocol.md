# Manual evaluation protocol

## 1. Declare the condition

Record the task ID, repository revision, Python environment, Bob client and
version, active mode, and relevant configuration. If comparing a workflow with
an alternative, describe the difference precisely. Do not assume the model is
fixed or visible when the client routes requests automatically.

The result template is a reporting aid, not a machine-enforced scorecard. Use
`null` for information you could not observe. Separate a model run's metrics
from the helper's local test metrics.

## 2. Start fresh

Use the helper to prepare a new workspace. Confirm the baseline before giving
the task to an agent. Keep the original fixture unchanged. Start a fresh
conversation and note any global or project rules that could affect the run.

Use the same task prompt and acceptance criteria for comparable attempts.
Repeated exposure can make the task easier; record run order and prior exposure
rather than claiming independence without evidence.

## 3. Observe the participant

Let the participant work within the stated scope and native permissions.
Record the start and end times, interventions, retries, and whether work was
abandoned. Do not silently substitute an edited prompt or manually repaired
candidate and present it as an uninterrupted agent result.

Do not require a complex workflow for a small task. Evaluate whether the work
was proportionate and evidence-based, not whether it used every available tool.

## 4. Validate independently

Run the helper's `candidate` command from this evaluation repository against
the participant's workspace. It runs the trusted original public tests in a
separate local Python process. A subprocess provides execution separation, not
a security sandbox.

Inspect the diff, review any changed tests, and run relevant additional checks
separately. Complete the manual acceptance checklist. The helper's pass means
the public tests passed; it cannot establish all qualitative criteria.

Preserve raw helper reports locally. Each report records file fingerprints and
test output. Keep the command, result, and relevant revision together so an
outdated pass cannot be mistaken for the state of a later candidate.

## 5. Report without overclaiming

Use `results/result-template.json` for each participant attempt. Link the
baseline/candidate reports and diff, and describe any redactions. Keep failed,
incomplete, and abandoned runs visible in a comparison.

Useful observations include the task outcome, actual agent wall time, manual
interventions, reported resource use if available, and scope of validation.
Do not convert test-execution time into agent duration or use a missing cost
measurement as zero cost.

This repository starts with one tiny public fixture. A successful example is
not a large-project benchmark. A controlled comparison would need enough tasks
and repeated runs, a declared protocol, comparable conditions, and analysis of
uncertainty before supporting general conclusions. No such study is included.
