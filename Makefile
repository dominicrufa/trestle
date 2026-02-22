.PHONY: setup-uv setup-conda lock lint format test check

setup-uv:
	uv sync --extra dev --extra notebooks --extra viz

setup-conda:
	micromamba create -f environment.yml

lock:
	uv lock

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run pytest

check: lint test
