# Result records

No participant run or aggregate benchmark result is included yet.

Copy `result-template.json` for each real run. Keep unknown values as `null` and
retain `not_run` or `not_assessed` until evidence exists. The template itself is
not a result.

The offline helper writes a separate evidence report for baseline and candidate
checks. Reference those reports from the participant record; do not confuse
their test duration with the agent's task duration.

Generated local workspaces and reports can live under the git-ignored `runs/`
directory. Before contributing a record, remove credentials, confidential code,
private paths, and unrelated conversation content. Explain redactions and
include enough evidence to assess the specific claim. Review the participant's
code and test changes before recording manual acceptance.
