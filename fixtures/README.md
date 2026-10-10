# Fixtures

`tiny-ledger/` is the original deliberately faulty Python example copied from
the companion `bob-workflow-kit` project. The files are kept unchanged so the
same starting task can be used across both projects.

The upstream source is
<https://github.com/Saqlain1999/bob-workflow-kit/tree/main/examples/tiny-ledger>.


Keep this original intact. Prepare a disposable copy with:

```sh
python scripts/evaluate.py prepare --output runs/ledger-001
```

The original fixture has nine tests and one intentional failure. Do not include
it in a blanket command that assumes every discovered test should pass. The
helper's `baseline` command checks that the known failure remains reproducible.
