# Preparation validation

Recorded 10 October 2026 (Europe/Dublin). This is a local preparation record, not a participant benchmark result.

| Check | Observed result |
| --- | --- |
| Offline helper suite on Linux, Python 3.12.14 | 9 tests passed with exit code 0 |
| Original fixture baseline | Nine public tests; eight passed and the intended missing-recipient atomicity regression failed |
| Fixture integrity | All four fixture files matched the Workflow Kit example byte for byte |
| Participant result template | Parses as JSON; no-run status retained |

The helper suite exercises fresh preparation, preservation of existing files, the expected baseline, a failing candidate, a focused temporary repair, changed candidate tests, timeout reporting, and rejection of invalid timeout limits. A temporary repaired fixture inside a software test is not a live agent evaluation.

The GitHub Actions definition runs the helper suite. Hosted CI has not been executed during preparation. Native Windows/macOS execution, Python 3.8 runtime compatibility, live Bob behavior, and large-repository evaluations are not established by this record.

Use the [evaluation protocol](docs/protocol.md) to collect an actual participant run. Keep helper test results, participant behavior, and manual acceptance separate.
