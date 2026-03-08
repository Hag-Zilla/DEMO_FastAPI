.PHONY: help init run test lint format bootstrap-admin clean

help:
	@echo "Usage: make <target>"
	@echo "Targets: init, run, test, lint, format, bootstrap-admin, clean"

# Wrapper (interactive) for setup.sh which handles conda/venv flows
init:
	bash setup.sh

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
