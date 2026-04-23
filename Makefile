.PHONY: help init init-env sync lock run test lint format bootstrap-admin clean install-hooks run-hooks run-hooks-staged update-hooks clean-hooks

UV_PACKAGE := demo-fastapi-api

help:
	@echo "=== DEVELOPMENT (Local) ==="
	@echo "  make init             Setup uv environment for the API service (.venv + runtime deps)"
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

# uv-only environment setup (creates .venv if needed, then sync runtime deps)
init:
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "Error: uv is required. Install it from https://docs.astral.sh/uv/"; \
		exit 1; \
	fi
	@if [ ! -d .venv ]; then \
		echo "Creating .venv with uv..."; \
		uv venv; \
	fi
	uv sync --package $(UV_PACKAGE)

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
	uv sync --package $(UV_PACKAGE)

# Sync all dependencies including dev tools (pre-commit, pytest, ruff, mypy, etc.)
sync-dev:
	uv sync --package $(UV_PACKAGE) --extra dev --all-groups

# Refresh uv lockfile
lock:
	uv lock

# Run in development mode (auto-reload)
run:
	uv run --package $(UV_PACKAGE) uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000

test:
	uv run --package $(UV_PACKAGE) pytest -W ignore::ResourceWarning:anyio

lint:
	uv run --package $(UV_PACKAGE) ruff check services/api

format:
	uv run --package $(UV_PACKAGE) ruff format services/api

# Admin bootstrap (interactive)
bootstrap-admin:
	uv run --package $(UV_PACKAGE) bash startup/project_spec.sh

clean:
	find . -type f -name "*.pyc" -delete
	rm -rf __pycache__ .pytest_cache .mypy_cache build dist

# Contract testing (Schemathesis — requires no running server, tests via ASGI)
contract-test:
	@echo "Running Schemathesis contract tests..."
	uv run --package $(UV_PACKAGE) pytest services/api/tests/test_contract.py -v

# Load testing (Locust — requires a running API server)
load-test:
	@echo "Starting Locust load test against http://localhost:8000 ..."
	@echo "  Use --users / --spawn-rate / --run-time --headless for CI mode."
	uv run --package $(UV_PACKAGE) locust -f services/api/tests/load_tests/locustfile.py --host http://localhost:8000

# Headless load test (CI-friendly, 20 users, 60 s)
load-test-headless:
	uv run --package $(UV_PACKAGE) locust -f services/api/tests/load_tests/locustfile.py --host http://localhost:8000 \
		--users 20 --spawn-rate 5 --run-time 60s --headless

# ============================================================================
# Code Quality & Git Hooks
# ============================================================================

install-hooks:
	@echo "Installing pre-commit hooks..."
	uv run --package $(UV_PACKAGE) pre_commit install
	uv run --package $(UV_PACKAGE) pre_commit install-hooks
	@echo "✓ Pre-commit hooks installed"

run-hooks:
	@echo "Running pre-commit hooks on all files..."
	uv run --package $(UV_PACKAGE) pre_commit run --all-files

run-hooks-staged:
	@echo "Running pre-commit hooks on staged files..."
	uv run --package $(UV_PACKAGE) pre_commit run

update-hooks:
	@echo "Updating pre-commit hooks to latest versions..."
	uv run --package $(UV_PACKAGE) pre_commit autoupdate
	@echo "✓ Hooks updated. Review changes in .pre-commit-config.yaml"

clean-hooks:
	@echo "Cleaning pre-commit cache..."
	uv run --package $(UV_PACKAGE) pre_commit clean
	uv run --package $(UV_PACKAGE) pre_commit clean-files
