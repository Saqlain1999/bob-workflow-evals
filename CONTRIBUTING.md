# Contributing

This repository starts with one small, public coding task. Contributions should
improve repeatability or add well-defined tasks, not imply benchmark coverage
that has not been measured.

## Improve the helper or documentation

Use Python 3.8+ and the standard library. Preserve the existing commands and
report semantics unless a change is explicitly documented. Add a meaningful
test for changed behaviour, then run from the repository root:

```sh
python -m unittest discover -s tests -v
```

Keep helper tests separate from fixture tests, which deliberately contain a
baseline failure. Do not repair the original fixture as incidental cleanup.

Explain the problem, the proposed change, and the observed checks. Avoid
unnecessary package dependencies, model SDKs, credentials, and network calls.

## Propose a task

A task contribution needs:

- A clearly licensed, self-contained starting fixture.
- A task identifier and observable acceptance criteria.
- A reproducible faulty or incomplete baseline.
- A prompt describing the problem without giving the patch.
- Checks that detect the target failure and a manual review checklist.
- A description of what the task does and does not measure.

Keep fixtures small enough to inspect. If a task requires services or special
hardware, state that before anyone begins. Do not claim a task represents
large-repository work merely because it generates many files.

## Submit a participant run

Use `results/result-template.json` and follow `docs/protocol.md`. Report the
condition, client/version information that is actually visible, the prompt,
fresh-start procedure, attempts, interventions, validation evidence, and
limitations. Include failed and abandoned attempts in comparisons.

Use `null` for unavailable measurements. Test time, agent wall time, token usage,
and cost are different measurements. Do not substitute one for another.

Share only material you are entitled to publish. Remove credentials, private
paths, organization data, and conversation content that is not part of the
public exercise. Record any redactions so reviewers understand the evidence
limits. A result report is a claim to review, not a trusted leaderboard entry.

## Licensing and attribution

Your original contribution is offered under this repository's MIT License.
Keep third-party notices intact and identify the source and license of any
copied material. Product names and links do not imply vendor endorsement.
