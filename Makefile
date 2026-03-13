.PHONY: help init init-uv init-venv sync lock run test lint format bootstrap-admin clean

help:
	@echo "Usage: make <target>"
	@echo "Targets: init, init-uv, init-venv, sync, lock, run, test, lint, format, bootstrap-admin, clean"

# Wrapper (interactive) for setup.sh (default: uv)
init:
	bash setup.sh

init-uv:
	printf "uv\n" | bash setup.sh

init-venv:
	printf "venv\n" | bash setup.sh

# Sync dependencies from pyproject.toml/uv.lock
sync:
	uv sync

# Refresh uv lockfile
lock:
	uv lock

# Export a pinned requirements.txt from uv.lock (uv must be installed).
# Tries a couple of common uv export invocations and prints guidance if none work.
export-reqs: lock
	@echo "Exporting pinned requirements.txt from uv.lock"
	@if command -v uv >/dev/null 2>&1; then \
		(set -e; \
		 uv lock || true; \
		 if uv export -f requirements.txt >/dev/null 2>&1; then \
			 uv export -f requirements.txt; \
		 elif uv export --format=requirements.txt -o requirements.txt >/dev/null 2>&1; then \
			 uv export --format=requirements.txt -o requirements.txt; \
		 else \
			 echo "uv does not support a direct 'export requirements' subcommand on this version."; \
			 echo "Please run 'uv export' manually or generate requirements.txt from the lock using uv's documented syntax."; \
			 exit 1; \
		 fi); \
		echo "wrote requirements.txt from uv.lock"; \
	else \
		echo "uv is not installed; cannot export requirements.txt from uv.lock"; \
		echo "Install uv or create a pinned requirements.txt manually."; \
		exit 1; \
	fi

# Run in development mode (auto-reload)
run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test:
	pytest -q

lint:
	flake8 app

format:
	black app

# Admin bootstrap (interactive)
bootstrap-admin:
	bash project_spec.sh

clean:
	find . -type f -name "*.pyc" -delete
	rm -rf __pycache__ .pytest_cache .mypy_cache build dist
