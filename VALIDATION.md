# Preparation validation

Recorded 10 October 2026 (Europe/Dublin). This is a local preparation record, not a participant benchmark result.

| Check | Observed result |
| --- | --- |
| Offline helper suite on Linux, Python 3.12.14 | 9 tests passed with exit code 0 |
| Original fixture baseline | Nine public tests; eight passed and the intended missing-recipient atomicity regression failed |
| Fixture integrity | All four fixture files matched the Workflow Kit example byte for byte |
| Participant result template | Parses as JSON; no-run status retained |

The helper suite exercises fresh preparation, preservation of existing files, the expected baseline, a failing candidate, a focused temporary repair, changed candidate tests, timeout reporting, and rejection of invalid timeout limits. A temporary repaired fixture inside a software test is not a live agent evaluation.

## Hosted publication checks

[GitHub Actions run 38008089567](https://github.com/Saqlain1999/bob-workflow-evals/actions/runs/38008089567) completed successfully for published commit `7291d345aa9507cf5d4e07a1557959202ea922c6` on 10 October 2026 (UTC). Both helper-test jobs passed on `ubuntu-latest`, using Python 3.10 and 3.12. The recorded test step was **Run helper tests in temporary workspaces**.

These hosted software checks are separate from the local preparation and from participant benchmarks. Native Windows/macOS execution, Python 3.8 runtime compatibility, live Bob behavior, and large-repository evaluations are not established by this record.

Use the [evaluation protocol](docs/protocol.md) to collect an actual participant run. Keep helper test results, participant behavior, and manual acceptance separate.
