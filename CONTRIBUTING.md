# Contributing

Thanks for helping improve `termad`.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
```

## Local quality checks

```bash
pytest
python -m build
python -m twine check dist/*
```

## Manual demo checks (real TTY)

Run these in macOS Terminal or iTerm2 (not an IDE output pane):

```bash
python examples/demo_cli.py --quick
python examples/demo_claude_code.py --quick
python examples/demo_open_claw.py --quick
```

## Scope and platform

- Runtime target for v1 is macOS terminal environments.
- Keep public API stable unless a change is documented in `CHANGELOG.md`.
- Avoid introducing non-stdlib runtime dependencies without maintainers' approval.

## Pull request expectations

- Keep changes focused and include tests for behavior changes.
- Update `README.md` and `CHANGELOG.md` when public behavior changes.
- Ensure CI is green before requesting review.
