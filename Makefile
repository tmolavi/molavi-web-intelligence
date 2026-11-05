.PHONY: install test lint format run-api run-mcp benchmark clean

install:
	pip install -e ".[dev]"

test:
	PYTHONPATH=src pytest tests -v

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

run-api:
	uvicorn mwie.api.app:app --host 0.0.0.0 --port 8000 --reload

run-mcp:
	python3 -m mwie.mcp.server

benchmark:
	python3 scripts/run_benchmarks.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
