.PHONY: help init init-uv init-venv init-env sync lock export-reqs run test lint format bootstrap-admin clean install-hooks run-hooks run-hooks-staged update-hooks clean-hooks

PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif [ -x venv/bin/python ]; then echo venv/bin/python; else echo python3; fi)

help:
	@echo "=== DEVELOPMENT (Local) ==="
	@echo "  make init             Setup environment (interactive, defaults to uv)"
	@echo "  make init-uv          Setup with uv"
	@echo "  make init-venv        Setup with venv (pip)"
	@echo "  make init-env         Create .env files from templates (.example)"
	@echo "  make sync             Install/sync dependencies from uv.lock"
	@echo "  make sync-dev         Install all dependencies including dev tools (pre-commit, pytest, ruff, mypy)"
	@echo "  make run              Start FastAPI dev server (auto-reload)"
	@echo "  make test             Run pytest suite"
	@echo "  make lint             Run ruff linting"
	@echo "  make format           Format code with ruff"
	@echo ""
	@echo "=== DEPENDENCY MANAGEMENT ==="
	@echo "  make lock             Refresh uv.lock"
	@echo "  make export-reqs      Export requirements.txt from uv.lock"
	@echo ""
	@echo "  make contract-test    Run Schemathesis contract / property tests"
	@echo "  make load-test        Start Locust load test (interactive, needs running API)"
	@echo "  make load-test-headless Run Locust headless (CI mode, 20u/60s)"
	@echo ""
	@echo "=== CODE QUALITY & GIT HOOKS ==="
	@echo "  make install-hooks    Install pre-commit hooks"
	@echo "  make run-hooks        Run all hooks on all files"
	@echo "  make run-hooks-staged Run hooks on staged files only"
	@echo "  make update-hooks     Update hooks to latest versions"
	@echo "  make clean-hooks      Clean pre-commit cache"
	@echo ""
	@echo "=== MAINTENANCE ==="
	@echo "  make bootstrap-admin  Bootstrap admin user (interactive)"
	@echo "  make clean            Remove Python cache files"
	@echo "  make help             Show this help message"

# Wrapper (interactive) for setup.sh (default: uv)
init:
	bash startup/setup.sh

init-uv:
	printf "uv\n" | bash startup/setup.sh

init-venv:
	printf "venv\n" | bash startup/setup.sh

# Create .env files from .example templates (safe, won't overwrite existing)
init-env:
	@echo "=== Environment Files Setup ==="
	@echo ""
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✓ Created .env from .env.example"; \
	else \
		echo "✗ .env already exists (skipping)"; \
	fi
	@echo ""
	@echo "Next steps:"; \
	echo "  1. Edit your .env files with actual values"; \
	echo "  2. For local dev: nano .env"; \
	echo ""

# Sync dependencies from pyproject.toml/uv.lock
sync:
	uv sync

# Sync all dependencies including dev tools (pre-commit, pytest, ruff, mypy, etc.)
sync-dev:
	uv sync --extra dev --all-groups

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
	$(PYTHON) -m uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000

test:
	pytest --tb=short -W ignore::ResourceWarning:anyio

lint:
	$(PYTHON) -m ruff check services/api

format:
	$(PYTHON) -m ruff format services/api

# Admin bootstrap (interactive)
bootstrap-admin:
	bash startup/project_spec.sh

clean:
	find . -type f -name "*.pyc" -delete
	rm -rf __pycache__ .pytest_cache .mypy_cache build dist

# Contract testing (Schemathesis — requires no running server, tests via ASGI)
contract-test:
	@echo "Running Schemathesis contract tests..."
	pytest services/api/tests/test_contract.py -v

# Load testing (Locust — requires a running API server)
load-test:
	@echo "Starting Locust load test against http://localhost:8000 ..."
	@echo "  Use --users / --spawn-rate / --run-time --headless for CI mode."
	locust -f services/api/tests/load_tests/locustfile.py --host http://localhost:8000

# Headless load test (CI-friendly, 20 users, 60 s)
load-test-headless:
	locust -f services/api/tests/load_tests/locustfile.py --host http://localhost:8000 \
		--users 20 --spawn-rate 5 --run-time 60s --headless

# ============================================================================
# Code Quality & Git Hooks
# ============================================================================

install-hooks:
	@echo "Installing pre-commit hooks..."
	$(PYTHON) -m pre_commit install
	$(PYTHON) -m pre_commit install-hooks
	@echo "✓ Pre-commit hooks installed"

run-hooks:
	@echo "Running pre-commit hooks on all files..."
	$(PYTHON) -m pre_commit run --all-files

run-hooks-staged:
	@echo "Running pre-commit hooks on staged files..."
	$(PYTHON) -m pre_commit run

update-hooks:
	@echo "Updating pre-commit hooks to latest versions..."
	$(PYTHON) -m pre_commit autoupdate
	@echo "✓ Hooks updated. Review changes in .pre-commit-config.yaml"

clean-hooks:
	@echo "Cleaning pre-commit cache..."
	$(PYTHON) -m pre_commit clean
	$(PYTHON) -m pre_commit clean-files
