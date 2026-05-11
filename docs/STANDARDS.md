# Development Standards

This document records the **architectural decisions and project-level policies** that
apply to every repository using MyBro. It is the authoritative reference for humans
and is automatically injected into Copilot context via `copilot-instructions.md`.

> **Template** - Adapt every section to your project before committing.
> Remove sections that do not apply. Document deviations explicitly.

**Scope**: decisions and policies only. Code patterns and examples belong in
`.github/instructions/*.instructions.md`.

---

## Table of Contents

1. [Stack and Tooling](#stack-and-tooling)
2. [Target Architecture](#target-architecture)
3. [Target Directory Structure](#target-directory-structure)
4. [Code Style Policy](#code-style-policy)
5. [Testing Policy](#testing-policy)
6. [Security Policy](#security-policy)
7. [Data Engineering Policy](#data-engineering-policy)
8. [API Design Policy](#api-design-policy)
9. [Observability Policy](#observability-policy)
10. [Branch and Release Strategy](#branch-and-release-strategy)

---

## Stack and Tooling

| Concern | Decision |
| --- | --- |
| Language | Python ≥ 3.11 |
| API framework | FastAPI ≥ 0.110 |
| Data validation | Pydantic v2 |
| ORM | SQLAlchemy + Alembic for migrations |
| DataFrame validation | Pandera |
| Experiment tracking | MLflow |
| Data versioning | DVC |
| Formatter / Linter | ruff (replaces black, isort, flake8) |
| Test runner | pytest |
| Dependency management | uv |
| Pre-commit hooks | pre-commit |

Deviations from this stack require an explicit decision record in this file.

---

## Target Architecture

The default target architecture is a layered, modular service with clear boundaries.

| Layer | Responsibility | Decision |
| --- | --- | --- |
| API | HTTP contract, validation, auth checks | FastAPI routers + Pydantic schemas |
| Application | Orchestration and use-case flows | Stateless service classes |
| Domain | Business rules and invariants | Pure Python logic, framework-agnostic |
| Data | Persistence and migrations | SQLAlchemy ORM + Alembic |
| Platform | Observability and config | Prometheus metrics + structured logging |

- Dependency direction is inward only (API -> Application -> Domain).
- Domain layer must not import framework, database, or network clients.
- External integrations (DB, queues, APIs) are isolated behind adapters.
- Cross-cutting concerns (auth, logging, tracing) are centralized and reusable.

---

## Target Directory Structure

Repository structure is a project-level decision and must follow these constraints:

- Separate source code, tests, docs, scripts, and assets at top level.
- Keep business logic isolated from framework and infrastructure concerns.
- Enforce predictable naming and package boundaries for generated code.

Detailed layout, naming conventions, and file placement rules are defined in:
`.github/instructions/project-structure.instructions.md`.

---

## Code Style Policy

- Follow PEP 8. `ruff format` and `ruff check` are the enforcement tools — do not
  override their output manually.
- Maximum function length: 50 lines. Extract helpers when exceeded.
- All public functions and classes must have a Google-style docstring (Args, Returns,
  Raises).
- Type hints are required on all function signatures.
- No magic numbers inline — use named constants.
- No `print` in production code — use `logging`.

---

## Testing Policy

- Minimum coverage target: 80% on critical modules.
- Unit tests must be pure (no I/O, no network, no DB).
- Integration tests that require external services go in `tests/integration/`.
- Every new public function must have at least a happy-path test and one error-path test.
- Test naming: `test_<function>_<scenario>` (e.g., `test_create_user_duplicate_email`).

---

## Security Policy

- All secrets loaded via `pydantic-settings` and typed as `SecretStr`. Never hardcoded.
- Add `.env` to `.gitignore`; provide `.env.example` with placeholder values only.
- JWT access token expiry ≤ 15 minutes; use refresh tokens for sessions.
- Authentication via `OAuth2PasswordBearer` + `Depends(get_current_user)` only.
- HTTP 401 for invalid credentials, HTTP 403 for insufficient permissions. Never HTTP 404
  on auth failures (information leakage).
- All SQL queries must use parameterized values. String interpolation for SQL is
  prohibited.

---

## Data Engineering Policy

- All pipelines must be idempotent: running twice must produce the same result.
- Prefer incremental loads over full reloads; use watermarks or partition keys.
- Failed records must be routed to a dead-letter table. Silent discard is prohibited.
- Log row counts at the entry and exit of every pipeline step.
- Schema migrations via Alembic only. Never modify the database schema manually.
- All migrations must be reversible (`upgrade` + `downgrade`).

---

## API Design Policy

- One `APIRouter` per business domain. No monolithic router files.
- All endpoints must have an explicit `status_code`.
- Exception hierarchy: define a base `APIError` and map subclasses to HTTP codes in a
  shared exception handler — not inline in route functions.
- CORS must be explicitly configured. Permissive defaults (`allow_origins=["*"]`) are
  prohibited in production.

---

## Observability Policy

- Use the `logging` module with structured JSON output (compatible with Loki).
- Prometheus metrics defined at module level, never inside functions.
- Metric labels must be low-cardinality (method, endpoint, status code). User IDs and
  raw URLs as labels are prohibited.
- All services must expose a `/metrics` endpoint.

---

## Branch and Release Strategy

| Branch | Purpose |
| --- | --- |
| `main` | Production-stable. Protected. Merge via PR only. |
| `develop` | Integration branch. All feature branches merge here first. |
| `feature/<ticket>-<description>` | One branch per feature or fix. |

- All PRs must have CI green before merge.
- Commit messages: `feat:`, `fix:`, `chore:`, `docs:` prefix required.
- Releases are tagged on `main` with semver (`v1.2.3`).

---

Last updated: 2026-05-11
