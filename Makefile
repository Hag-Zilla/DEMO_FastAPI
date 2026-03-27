.PHONY: help init init-uv init-venv init-env sync lock export-reqs run test lint format bootstrap-admin clean docker-build docker-up docker-down docker-logs docker-test docker-shell docker-clean prometheus grafana metrics install-hooks run-hooks run-hooks-staged update-hooks clean-hooks

PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif [ -x venv/bin/python ]; then echo venv/bin/python; else echo python3; fi)

help:
	@echo "=== DEVELOPMENT (Local) ==="
	@echo "  make init             Setup environment (interactive, defaults to uv)"
	@echo "  make init-uv          Setup with uv"
	@echo "  make init-venv        Setup with venv (pip)"
	@echo "  make init-env         Create .env files from templates (.example)"
	@echo "  make sync             Install/sync dependencies from uv.lock"
	@echo "  make run              Start FastAPI dev server (auto-reload)"
	@echo "  make test             Run pytest suite"
	@echo "  make lint             Run flake8 linting"
	@echo "  make format           Format code with black"
	@echo ""
	@echo "=== DEPENDENCY MANAGEMENT ==="
	@echo "  make lock             Refresh uv.lock"
	@echo "  make export-reqs      Export requirements.txt from uv.lock"
	@echo ""
	@echo "=== DOCKER (Production) ==="
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start containers (docker-compose up -d)"
	@echo "  make docker-down      Stop containers (docker-compose down)"
	@echo "  make docker-logs      View container logs (follow mode)"
	@echo "  make docker-test      Run tests inside containers"
	@echo "  make docker-shell     Open bash shell in app container"
	@echo "  make docker-clean     Cleanup Docker artifacts"
	@echo ""
	@echo "=== MONITORING ==="
	@echo "  make prometheus       Open Prometheus UI (http://localhost:9090)"
	@echo "  make grafana          Open Grafana UI (http://localhost:3000)"
	@echo "  make metrics          View raw metrics endpoint (http://localhost:8000/metrics)"
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
	bash setup.sh

init-uv:
	printf "uv\n" | bash setup.sh

init-venv:
	printf "venv\n" | bash setup.sh

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
	@if [ ! -f .env.docker.dev ]; then \
		cp .env.docker.dev.example .env.docker.dev; \
		echo "✓ Created .env.docker.dev from .env.docker.dev.example"; \
	else \
		echo "✗ .env.docker.dev already exists (skipping)"; \
	fi
	@if [ ! -f .env.docker.prod ]; then \
		cp .env.docker.prod.example .env.docker.prod; \
		echo "✓ Created .env.docker.prod from .env.docker.prod.example"; \
		echo "⚠️  WARNING: Edit .env.docker.prod with real secrets before deploying!"; \
	else \
		echo "✗ .env.docker.prod already exists (skipping)"; \
	fi
	@echo ""
	@echo "Next steps:"; \
	echo "  1. Edit your .env files with actual values"; \
	echo "  2. For dev local: nano .env"; \
	echo "  3. For dev docker: nano .env.docker.dev"; \
	echo "  4. For production: nano .env.docker.prod"; \
	echo ""

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
	$(PYTHON) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

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

# ============================================================================
# Docker targets (Production/Deployment)
# ============================================================================

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo ""
	@echo "✓ Services started. Check status with: make docker-logs"
	@echo "  - Nginx (reverse proxy): http://localhost"
	@echo "  - FastAPI (app): http://localhost/docs"
	@echo "  - Redis (internal): 6379"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f app

docker-test:
	@echo "Running tests inside app container..."
	docker-compose exec app pytest -q

docker-clean:
	@echo "Cleaning up Docker artifacts..."
	docker-compose down --volumes
	docker system prune -f
	@echo "✓ Docker cleanup complete"

docker-shell:
	docker-compose exec app /bin/bash

# ============================================================================
# Monitoring & Observability
# ============================================================================

prometheus:
	@echo "Opening Prometheus UI..."
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:9090; \
	elif command -v open >/dev/null 2>&1; then \
		open http://localhost:9090; \
	else \
		echo "Prometheus UI: http://localhost:9090"; \
	fi

grafana:
	@echo "Opening Grafana UI..."
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:3000; \
	elif command -v open >/dev/null 2>&1; then \
		open http://localhost:3000; \
	else \
		echo "Grafana UI: http://localhost:3000"; \
	fi

metrics:
	@echo "Fetching raw metrics from FastAPI..."
	curl -s http://localhost:8000/metrics | head -50
	@echo "\n\n(Showing first 50 lines. For all metrics: curl http://localhost:8000/metrics)"

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
