.PHONY: help init init-env sync sync-api sync-all lock run test lint format prestart init-data export-openapi bootstrap-admin clean install-hooks run-hooks run-hooks-staged update-hooks clean-hooks migrate migrate-create migrate-check
UV_PACKAGE := demo-fastapi-api

help:
	@echo "=== DEVELOPMENT (Local) ==="
	@echo "  make init             Setup .venv and install runtime deps for all services"
	@echo "  make init-env         Create .env files from templates (.example)"
	@echo "  make sync             A – runtime deps of ALL services"
	@echo "  make sync-api         B – runtime deps of the API service only"
	@echo "  make sync-all         Alias of make sync"
	@echo "  make run              Start FastAPI dev server (auto-reload)"
	@echo "  make test             Run pytest suite"
	@echo "  make lint             Run ruff linting"

	@echo "  make format           Format code with ruff"
	@echo ""
	@echo "=== DEPENDENCY MANAGEMENT ==="
	@echo "  make lock             Refresh uv.lock"
	@echo "  make migrate          Apply Alembic migrations to head"
	@echo "  make migrate-create   Create Alembic revision (set MSG='your message')"
	@echo "  make migrate-check    Fail if migrations are out of sync"
	@echo "  make export-openapi   Export OpenAPI schema to services/data/openapi.json"
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
	@echo "  make prestart         Run DB readiness checks"
	@echo "  make init-data        No-op helper (use make bootstrap-admin)"
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
	$(MAKE) sync

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

# Sync runtime dependencies for all workspace services from pyproject.toml/uv.lock
sync:
	uv sync --no-group tools

# Sync runtime dependencies for the API service only
sync-api:
	uv sync --package $(UV_PACKAGE)

# Alias for syncing runtime dependencies of all workspace services
sync-all:
	$(MAKE) sync

# Refresh uv lockfile
lock:
	uv lock

# Apply database migrations
migrate:
	uv run --package $(UV_PACKAGE) alembic -c services/api/alembic.ini upgrade head

# Create a new migration revision (usage: make migrate-create MSG="add field")
migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: provide MSG, e.g. make migrate-create MSG='add xyz'"; \
		exit 1; \
	fi
	uv run --package $(UV_PACKAGE) alembic -c services/api/alembic.ini revision --autogenerate -m "$(MSG)"

migrate-check:
	uv run --package $(UV_PACKAGE) alembic -c services/api/alembic.ini check

# Run in development mode (auto-reload)
run:
	uv run --package $(UV_PACKAGE) uvicorn services.api.main:app --reload --host 127.0.0.1 --port 8000

test:
	uv run --package $(UV_PACKAGE) pytest -W ignore::ResourceWarning:anyio

lint:
	uv run --package $(UV_PACKAGE) ruff check services/api

format:
	uv run --package $(UV_PACKAGE) ruff format services/api

prestart:
	uv run --package $(UV_PACKAGE) python -m services.api.prestart

init-data:
	@echo "No automatic init-data bootstrap. Use: make bootstrap-admin"

export-openapi:
	uv run --package $(UV_PACKAGE) python -c "import json; from services.api.main import app; print(json.dumps(app.openapi(), indent=2))" > services/data/openapi.json

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
	uv run --only-group tools pre-commit install
	uv run --only-group tools pre-commit install-hooks
	@echo "✓ Pre-commit hooks installed"

run-hooks:
	@echo "Running pre-commit hooks on all files..."
	uv run --only-group tools pre-commit run --all-files

run-hooks-staged:
	@echo "Running pre-commit hooks on staged files..."
	uv run --only-group tools pre-commit run

update-hooks:
	@echo "Updating pre-commit hooks to latest versions..."
	uv run --only-group tools pre-commit autoupdate
	@echo "✓ Hooks updated. Review changes in .pre-commit-config.yaml"

clean-hooks:
	@echo "Cleaning pre-commit cache..."
	uv run --only-group tools pre-commit clean
	uv run --only-group tools pre-commit clean-files
