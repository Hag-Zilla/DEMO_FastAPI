FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Create required directories
RUN mkdir -p /app/data /app/logs

# Copy project files (build context is repo root)
COPY pyproject.toml uv.lock* ./
COPY app/ ./app/
COPY --chown=fastapi:fastapi data/ ./data/
COPY --chown=fastapi:fastapi logs/ ./logs/

# Install dependencies with uv
RUN uv sync --frozen

# Create non-root user
RUN useradd -m -u 1000 fastapi && chown -R fastapi:fastapi /app

USER fastapi

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD /app/.venv/bin/python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run app
CMD ["./.venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
