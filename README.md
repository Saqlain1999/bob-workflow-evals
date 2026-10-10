# Bob Workflow Evals

A small, reproducible evaluation starter for IBM Bob coding workflows.

The first task asks an agent to repair a deliberately faulty Python ledger.
The repository includes the original fixture, a public regression suite, a
participant prompt, a manual acceptance checklist, and an offline helper that
runs the trusted tests against a disposable candidate workspace.

**Status: evaluation starter. No live Bob evaluation or large-repository
benchmark has been performed for this repository.** The included task is a small
correctness exercise. Passing it does not establish reliable performance on
large projects, prove that a workflow caused an improvement, or guarantee future
results. This is an independent community project, not an IBM product.

## What is here

| Path | Purpose |
| --- | --- |
| `fixtures/tiny-ledger/` | Deliberately faulty original and its nine public tests |
| `tasks/tiny-ledger-atomicity/` | Task definition, agent prompt, and acceptance checklist |
| `scripts/evaluate.py` | Prepare a fresh workspace and collect local test evidence |
| `tests/test_evaluate.py` | Checks for the evaluation helper itself |
| `docs/protocol.md` | How to run and report a manual evaluation |
| `results/result-template.json` | Structured record for an actual participant run |

The fixture uses integer cents, in-memory state, and Python's standard library.
No packages, services, API keys, or network access are needed for its checks.
The helper makes no model calls. Running Bob is a separate, manual step using
the installation and account you already have.

## Quick start

Use Python 3.8 or later. The examples use `python`; use `python3` if that is the
executable name on your system. Run these commands from the repository root.

### 1. Check the helper

```sh
python -m unittest discover -s tests -v
```

This suite should pass. It is separate from the fixture's deliberately failing
test suite.

### 2. Prepare a disposable workspace

```sh
python scripts/evaluate.py prepare --output runs/ledger-001
```

The output directory must not already exist. Keep the original under
`fixtures/` unchanged, and use a new run directory for each independent attempt.

### 3. Verify the expected baseline

```sh
python scripts/evaluate.py baseline --workspace runs/ledger-001 --result runs/ledger-001-baseline.json
```

Expected helper status: `expected_baseline_failure`, exit code `0`.

The **underlying fixture suite** should run nine tests with eight passes and
one failure. The helper succeeds because it verified that specific faulty
baseline. This is not a claim that the application is correct.

To inspect the ordinary failing test output directly, change into the prepared
workspace and run:

```sh
python -m unittest discover -s tests -v
```

That direct command should exit with code `1` before the repair.

### 4. Run the task with Bob

Open `runs/ledger-001` as the workspace. Start a fresh Agent conversation and
paste [the task prompt](tasks/tiny-ledger-atomicity/AGENT_PROMPT.md). Record the
client version, active mode, relevant configuration, and whether the Workflow
Kit is installed. Do not assume those settings are identical across runs.

Let Bob investigate, modify the candidate, and report its verification evidence.
Use the existing public tests and documented behaviour. No large framework,
package installation, deployment, or external data is necessary.

### 5. Collect candidate evidence independently

Return to this repository's root and run:

```sh
python scripts/evaluate.py candidate --workspace runs/ledger-001 --result runs/ledger-001-candidate.json
```

Expected after a correct repair: `public_tests_passed`, exit code `0`.

The helper loads the public tests from this repository's original fixture and
runs them against the candidate's `ledger.py`. Editing or deleting tests inside
the candidate does not change that trusted test suite. The report includes
source and test fingerprints and flags whether the candidate's test files
differ from the original. Additional candidate tests require separate review
and execution; the helper does not silently count them as trusted checks.

**Public-test success is not final acceptance.** Complete the
[manual checklist](tasks/tiny-ledger-atomicity/ACCEPTANCE.md), inspect the diff,
and record the result using the [run template](results/result-template.json).

## What the helper reports

`--result` writes a JSON report and refuses to overwrite an existing report.
Without that option the report is printed to standard output. Test reports
include observed test counts, failures, errors, skip counts, output, execution
time, environment details, and file fingerprints. Time measured by the helper
is **test-execution time**, not the agent's task duration.

| Exit code | Meaning |
| --- | --- |
| `0` | Requested check succeeded: known faulty baseline confirmed, or public candidate tests passed |
| `1` | Tests ran, but the requested baseline or candidate condition was not satisfied |
| `2` | Invalid arguments, file/output error, timeout, or helper execution problem |

Each check has a 30-second timeout by default; override with a positive
`--timeout` value when needed. The helper executes local candidate Python code
as part of the test run. It is not a sandbox or a service for executing
untrusted submissions.

## Reporting an evaluation

Follow [the protocol](docs/protocol.md). Record actual observations rather than
the agent's own success claim. Keep missing metrics as `null`; do not infer
token usage, cost, or model identity from elapsed time or marketing labels.

For an exploratory comparison, start every attempt from a fresh fixture and a
fresh conversation. Change one condition at a time, preserve the same task and
acceptance criteria, and report all attempts. A single successful run is useful
as an example, not as evidence of broad superiority.

The local software checks are recorded in [VALIDATION.md](VALIDATION.md). No participant run or aggregate benchmark score is included. Contributions
should keep that distinction visible. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Companion projects

These public companion repositories have separate responsibilities. Check each project's status and validation notes before relying on a feature.

- [bob-workflow-kit](https://github.com/Saqlain1999/bob-workflow-kit): portable rules and a focused Bob workflow skill.
- [bob-workflow-runner](https://github.com/Saqlain1999/bob-workflow-runner): Controller design preview; no executable runner.
- [awesome-bob-workflows](https://github.com/Saqlain1999/awesome-bob-workflows): Curated workflow references with source and review-status metadata.

## License

Original repository content is provided under the [MIT License](LICENSE).
The Tiny Ledger fixture was copied from the companion Workflow Kit's original
example; its intentionally faulty baseline is preserved here. IBM Bob and any
other named products remain the property of their respective owners.
