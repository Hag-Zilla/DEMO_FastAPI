.PHONY: help init init-uv init-venv sync lock export-reqs run test lint format bootstrap-admin clean docker-build docker-up docker-down docker-logs docker-test docker-clean

PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; elif [ -x venv/bin/python ]; then echo venv/bin/python; else echo python3; fi)

help:
	@echo "=== DEVELOPMENT (Local) ==="
	@echo "  make init             Setup environment (interactive, defaults to uv)"
	@echo "  make init-uv          Setup with uv"
	@echo "  make init-venv        Setup with venv (pip)"
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
	@echo "  make docker-clean     Cleanup Docker artifacts"
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
