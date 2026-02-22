# Testing Guide

This project uses `pytest` for test execution.

## Test Categories

- Unit tests (`tests/test_nih_reporter_unit.py`)
- CLI tests (`tests/test_cli.py`)
- Smoke tests (`tests/test_smoke.py`)
- Live integration tests (`tests/test_nih_reporter_live.py`)

By default, only local/non-network tests run.

## Default Test Run (No External API Calls)

From the repository root:

```bash
uv run pytest
```

These tests use mocks for HTTP requests and are safe for regular local/CI runs.

## Live NIH RePORTER Integration Test (Opt-in)

The live test is skipped unless `NIH_REPORTER_LIVE=1` is set:

```bash
NIH_REPORTER_LIVE=1 PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_nih_reporter_live.py
```

Live-test behavior:

- Sends real requests to NIH RePORTER
- Enforces at least 1 second between requests
- Intended for occasional contract checks, not every CI run

## Troubleshooting

If you see `ModuleNotFoundError: No module named 'trestle'` after package/layout
changes, reinstall the local package into the environment:

```bash
uv sync --extra dev --reinstall
```
