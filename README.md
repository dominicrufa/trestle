Just some scaffolding

## Getting Started

Trestle uses `uv` as the primary Python package/dependency manager.

### Prerequisites

- Python 3.11
- `uv` installed
- `conda` installed (or `micromamba` as an alternative)

### Installation (uv, recommended)

```bash
git clone <repo-url>
cd trestle
uv sync
```

`uv sync` creates or updates the local virtual environment and installs
dependencies from `uv.lock`. Run project commands with `uv run <cmd>`.

### Installation (conda + uv)

```bash
conda env create --file environment.yml
conda activate trestle
uv sync
```

This path is for contributors who prefer conda/system-level package
management. Project dependency resolution remains driven by
`pyproject.toml` (and `uv.lock` once generated).
In this workflow, conda provides the base environment and `uv sync`
installs project Python packages.

### Installation (micromamba + uv)

```bash
micromamba create --file environment.yml
micromamba activate trestle
uv sync
```

This follows the same model: micromamba bootstraps the environment and
`uv sync` installs project Python packages from the lock/pyproject config.

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

## Testing

Run the default suite (no live NIH API calls):

```bash
uv run pytest
```

The default suite includes unit/CLI tests with mocked network behavior and
does not hit external services.

For a detailed testing guide, see:

- [`tests/README.md`](tests/README.md)

If imports or entry points look stale after local package/layout edits, force
reinstall before testing:

```bash
uv sync --extra dev --reinstall
```

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

## Docker

Build the image:

```bash
docker build -t trestle:latest .
```

Run a quick dependency smoke check:

```bash
docker run --rm trestle:latest
```

Run analysis code from your local checkout:

```bash
docker run --rm -it -v "$PWD":/app trestle:latest uv run python your_script.py
```
