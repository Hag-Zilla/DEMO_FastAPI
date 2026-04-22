# Local Run Guide

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Health Checks and Logs](#health-checks-and-logs)
- [Production Notes](#production-notes)
- [Troubleshooting](#troubleshooting)
- [References](#references)

## Overview

This repository is a simple FastAPI demo designed to run locally without Docker.

Default components:

1. FastAPI application
2. SQLite database
3. Redis (optional but recommended for shared cache/rate-limit storage)

## Prerequisites

- Python 3.13+
- `uv` (recommended) or `venv` + `pip`
- Optional: local Redis server on `127.0.0.1:6379`

## Quick Start

```bash
# 1) Initialize project and install dependencies
make init
make sync-dev

# 2) Create local env file
make init-env

# 3) Start API
make run
```

Main URLs:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Configuration

Edit `.env` and set at least:

- `SECRET_KEY`: JWT signing key
- `JWT_EXPIRATION_MINUTES`: token validity period
- `DATABASE_URL`: defaults to local SQLite path
- `REDIS_URL`: local Redis URL if available
- `DEBUG`: `true` for development, `false` for stricter behavior

## Health Checks and Logs

Health endpoints:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/health/live
curl -i http://127.0.0.1:8000/health/ready
```

Application logs:

```bash
tail -f services/api/logs/app.log
```

## Production Notes

This project is a demo. For production hardening, consider:

1. Managed database (PostgreSQL) instead of SQLite.
2. Managed Redis with auth and TLS.
3. Structured log shipping to a central backend.
4. Secret management (vault/KMS) instead of flat env files.
5. Host firewall and process supervision.

## Troubleshooting

### App fails at startup

Check logs and env values:

```bash
tail -n 200 services/api/logs/app.log
```

Common causes:

- Missing `SECRET_KEY`
- Invalid `DATABASE_URL`
- Invalid `REDIS_URL`

### Redis connectivity issues

If local Redis is installed:

```bash
redis-cli -h 127.0.0.1 -p 6379 ping
```

Expected result: `PONG`

### Port 8000 already in use

```bash
sudo ss -ltnp | grep ':8000'
```

Stop the conflicting process or run uvicorn on another port.

## References

- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/)
- [slowapi documentation](https://github.com/laurenceisla/slowapi)
- [Redis security guidance](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)
