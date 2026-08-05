# SmartStandard \u2014 language ports

Native Go / Node / Java / PHP re-implementations of `standard()` and
`conformance(root)`. Each reproduces the Python reference (`src/smartstandard/core.py`):
the deterministic `sha256:` standard hash and the 4-rule conformance score + drift.
Fixture trees under `conformance/fixtures/` exercise 100/75/25/0 scores.
Verify with `conformance/run.sh`.
