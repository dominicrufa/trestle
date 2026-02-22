# Examples

This directory contains usage examples for the NIH RePORTER CLI.

## Prerequisites

From the repo root:

```bash
uv sync --extra dev
```

## CLI Entry Point

The CLI command is exposed via `pyproject.toml` as:

```toml
[project.scripts]
trestle-nih-reporter = "trestle.api.cli:main"
```

Run it with `uv`:

```bash
uv run trestle-nih-reporter --help
```

## Example Commands

Basic request:

```bash
uv run trestle-nih-reporter
```

Filter by year and keyword:

```bash
uv run trestle-nih-reporter --year 2023 --keyword cancer --limit 10
```

Multiple years + keyword + activity code:

```bash
uv run trestle-nih-reporter --year 2022 --year 2023 --keyword "machine learning" --activity R01 --limit 25
```

Organization search with JSON and CSV output:

```bash
uv run trestle-nih-reporter \
  --org "STANFORD UNIVERSITY" \
  --year 2023 \
  --limit 5 \
  --out_json examples/results.json \
  --out_csv examples/results.csv
```

## Optional Direct Module Invocation

If you prefer module invocation:

```bash
PYTHONPATH=src .venv/bin/python -m trestle.api.cli --year 2023 --limit 5
```
