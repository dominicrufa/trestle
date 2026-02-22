Just some scaffolding

## Getting Started

Trestle uses `uv` as the primary Python package/dependency manager.

### Prerequisites

- Python 3.11
- `uv` installed
- Optional: conda/mamba if using the conda workflow

### Installation (uv, recommended)

```bash
git clone <repo-url>
cd trestle
uv sync
```

`uv sync` creates or updates the local virtual environment and installs
dependencies from `uv.lock`. Run project commands with `uv run <cmd>`.

### Installation (micromamba + uv)

```bash
micromamba create -f environment.yml
micromamba activate trestle
uv sync
```

This optional path is for contributors who prefer conda/system-level package
management. Project dependency resolution remains driven by
`pyproject.toml` and `uv.lock`.

If you use `conda` instead of `micromamba`, run:

```bash
conda env create -f environment.yml
conda activate trestle
uv sync
```

## Development Workflow

Common commands:

```bash
uv run pytest
uv run ruff check .
uv run ruff format .
```

If a `Makefile` is present, you can run:

```bash
make check
```

Typical loop:

- Sync the environment (`uv sync`).
- Run checks and tests (`uv run ...`).
- Update the lockfile only when dependency definitions change.

## Dependency Groups

When extras are defined in `pyproject.toml`, you can install optional groups:

- `dev`: lint/test tooling
- `notebooks`: notebook tooling
- `viz`: optional interactive visualization tooling

```bash
uv sync --extra dev
uv sync --extra notebooks
uv sync --extra viz
```
