<div align="center">

# Personal Expense Tracking API

A production-ready FastAPI demo showcasing a complete REST API for expense management with authentication, budgeting, and reporting.

**Built with:** FastAPI • SQLAlchemy • Pydantic • SQLite

</div>

![Python](https://img.shields.io/badge/python-3.14-blue.svg) ![FastAPI](https://img.shields.io/badge/framework-FastAPI-green.svg) ![Makefile](https://img.shields.io/badge/Makefile-✓-orange.svg) [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/Hag-Zilla/DEMO_FastAPI)](https://github.com/Hag-Zilla/DEMO_FastAPI/releases) [![CI](https://github.com/Hag-Zilla/DEMO_FastAPI/actions/workflows/ci-full.yml/badge.svg)](https://github.com/Hag-Zilla/DEMO_FastAPI/actions) [![codecov](https://codecov.io/github/Hag-Zilla/DEMO_FastAPI/graph/badge.svg?branch=develop)](https://app.codecov.io/github/Hag-Zilla/DEMO_FastAPI?branch=develop)

## 📑 Table of Contents

- [📖 About](#about)
- [✨ Features](#features)
- [🚀 Quick Start](#quick-start)
  - [Clone and Setup Environment](#clone-and-setup-environment)
  - [Essential Configuration Variables](#essential-configuration-variables)
  - [Build and Run Services](#build-and-run-services)
  - [Verify Installation](#verify-installation)
  - [Local Run Notes (No Docker)](#local-run-notes-no-docker)
  - [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
    - [Logging](#logging)
  - [Makefile & Common Tasks](#makefile--common-tasks)
  - [Running Tests](#running-tests)
  - [CI/CD & Automation](#cicd--automation)
  - [Scripts Management](#scripts-management)
- [📁 Project Structure](#project-structure)
- [📊 Data Structures](#data-structures)
  - [Enums](#enums)
  - [ORM Models & Database Schema](#orm-models--database-schema)
  - [API Request/Response Models](#api-requestresponse-models)
  - [Managing the Database](#managing-the-database)
  - [Database Migration](#database-migration)
- [🔌 API Endpoints](#api-endpoints)
  - [Role-Based Access Control](#role-based-access-control)
  - [Authentication](#authentication)
  - [User Management](#user-management)
  - [Expenses](#expenses)
  - [Reports](#reports)
  - [Alerts](#alerts)
  - [Analytics](#analytics)
  - [Health](#health)
- [🔐 Authentication & Authorization](#authentication--authorization)
  - [User Status Workflow](#user-status-workflow)
  - [Role Hierarchy](#role-hierarchy)
  - [Access Control Details](#access-control-details)
- [⚠️ Exception Handling](#exception-handling)
- [🛠️ Code Quality & Development Standards](#code-quality--development-standards)
- [📖 Extra documentation](#extra-documentation)
- [📚 Resources](#resources)
- [🤝 Contributing](#contributing)
- [💬 Support](#support)
- [📜 License](#-license)

---

## 📖 About
---

A personal expense tracking API built with **FastAPI** and **SQLite**. Users can manage their expenses, set monthly budgets, receive alerts for budget overruns, and generate detailed expense reports. The project demonstrates best practices in API design, authentication, database modeling, and production-ready application structure.

## ✨ Features
---

- **User Management**: Create accounts, OAuth2 authentication, role-based access control (admin/moderator/user)
- **User Approval Workflow**: Admin/Moderator review and approval of new user registrations (pending/active/disabled statuses)
- **Expense Tracking**: Add, update, delete expenses with typed categories and datetime tracking
- **Budget Management**: Set personal budgets with automatic tracking
- **Alerts**: Real-time detection of budget overruns
- **Reports**: Generate monthly and custom-period expense reports by category
- **Admin & Moderator Interface**: System-wide user and expense management with moderation capabilities
- **DDoS Protection**: App-level rate limiting with Redis-backed quota storage
- **Rate Limiting**: Distributed request rate limiting with slowapi and Redis
- **Error Handling**: Custom exception classes with proper HTTP status codes
- **Logging**: Console and file-based logging for monitoring
- **Type Validation**: Pydantic v2 with enums for categories and roles
- **Code Quality**: Pre-commit hooks, automated linting, type checking, and code standards enforcement

## 🚀 Quick Start
---

### Clone and Setup Environment

```bash
git clone <repo-url>
cd DEMO_FastAPI
make init-env      # Create .env from template
```

### Essential Configuration Variables

Edit `.env` with your configuration:

```bash
# Generate a SECRET_KEY first
openssl rand -hex 32

# Then edit:
nano .env
```

**Key variables in `.env`:**
- `SECRET_KEY` – JWT signing key (≥32 chars)
- `ALGORITHM` – JWT signing algorithm (`HS256`)
- `JWT_EXPIRATION_MINUTES` – Access token expiration in minutes
- `PASSWORD_RESET_EXPIRATION_MINUTES` – Password reset token expiration in minutes
- `DATABASE_URL` – SQLite path (default: `sqlite:///./services/data/expense_tracker.db`)
- `APP_NAME` – API title exposed in OpenAPI docs
- `APP_VERSION` – API version exposed in OpenAPI docs
- `DEBUG` – `true` for dev, `false` for production
- `ENVIRONMENT` – `local`, `staging`, or `production`
- `BACKEND_CORS_ORIGINS` – Allowed frontend origins for browser CORS requests

### Build and Run Services

```bash
make init          # Create .venv and install packages
source .venv/bin/activate
make install-hooks # Setup pre-commit checks
make run           # Start API at http://localhost:8000
```

**4. Access the API:**
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc
- Health check: http://localhost:8000/health

**5. Bootstrap admin user (optional):**
```bash
make bootstrap-admin    # Interactive password prompt
```

---

### Verify Installation

**Check if the API is running:**

```bash
curl http://localhost:8000/health
```

**Access the interactive API documentation:**

- **Swagger UI** (interactive form): http://localhost:8000/docs
- **ReDoc** (organized reference): http://localhost:8000/redoc
- **OpenAPI JSON** (schema): http://localhost:8000/openapi.json

To export the OpenAPI schema for external tools or client generation:
```bash
make export-openapi    # Generates services/data/openapi.json
```

**Available health check endpoints:**

```bash
# Liveness check
curl http://localhost:8000/health/live

# Readiness check (includes database ping)
curl http://localhost:8000/health/ready

# Startup phase check
curl http://localhost:8000/health/startup
```

**Example API request:**

```bash
curl -X POST "http://localhost:8000/api/v1/users/create-active" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secure123", "budget": 1000}'  # pragma: allowlist secret
```

### Local Run Notes (No Docker)

This demo is designed to run locally without Docker.

Default runtime stack:
- FastAPI application
- SQLite database
- Redis (optional, recommended for shared cache/rate-limiting storage)

Quick runtime checks:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/health/live
curl -i http://127.0.0.1:8000/health/ready
tail -f services/api/logs/app.log
```

If startup fails, validate `.env` first:
- `SECRET_KEY`
- `DATABASE_URL`
- `DEBUG`
- `REDIS_URL` (if configured)


### Configuration

#### Environment Variables

Environment variables & secrets

| File | Purpose |
|------|---------|
| `.env` | Dev local (FastAPI only) |

Settings are loaded via **Pydantic Settings** (`services/api/core/config.py`) with validation at startup.

- `SECRET_KEY` signs JWT tokens and must stay private.
- `ALGORITHM` defines the JWT signature algorithm (`HS256`).
- `JWT_EXPIRATION_MINUTES` controls access token lifetime.
- `PASSWORD_RESET_EXPIRATION_MINUTES` controls password-reset token lifetime.
- `DATABASE_URL` is the single source of truth for database connection.
- For SQLite, the app auto-creates the parent folder (default: `services/data/`).
- `APP_NAME` and `APP_VERSION` are used in generated API documentation metadata.
- `DEBUG` and `ENVIRONMENT` control runtime behavior (dev/staging/prod behavior).
- Use `make init` or `make sync` for all workspace services.
- Use `make sync-api` when you want the API service only.

##### `BACKEND_CORS_ORIGINS`

Defines which frontend origins are allowed to call the API from a browser.

Accepted formats:
- Single URL: `http://localhost:5173`
- Comma-separated list: `https://app.example.com,https://admin.example.com`
- JSON array string: `["https://app.example.com", "https://admin.example.com"]`

Behavior notes:
- This controls browser CORS checks (not server-to-server calls like `curl`/backend jobs).
- In local environment, if empty, the app falls back to `http://localhost:5173`.
- In production, explicitly list trusted frontend domains only.

#### Logging

Logs are written to:
- **Console**: For development feedback
- **File**: `services/api/logs/app.log`

Configured via YAML in `services/api/logs/config/logging.yaml`, loaded by `services/api/core/logging.py`.

### Makefile & Common Tasks

The project provides a comprehensive `Makefile` to simplify common workflows:

**Quick Commands:**
- `make init` — Create `.venv` and install runtime dependencies for all services
- `make sync` — Install runtime dependencies for all services
- `make sync-api` — Install runtime dependencies for the API service only
- `make migrate` — Apply Alembic migrations to the configured database
- `make migrate-create MSG="..."` — Create a new Alembic revision
- `make run` — Start the dev server
- `make test` — Run test suite
- `make run-hooks` — Run code quality checks
- `make help` — Show all available targets

**For all available Makefile targets** (development, quality checks, dependency management, etc.), see **[doc/DEVELOPMENT.md](doc/DEVELOPMENT.md#quick-reference)** or run:


### Running Tests

Comprehensive test suite covering unit, integration, contract, and load testing:

**Unit & Integration Tests**

Run the pytest suite:

```bash
# Run all tests
make test

# Run with coverage report
pytest --cov=services/api --cov-report=html

# Run specific test file
pytest services/api/tests/test_auth.py -v

# Run specific test class
pytest services/api/tests/test_users.py::TestAdminUserOperations -v
```

**Contract Testing (Schemathesis)**

Auto-generated property tests against OpenAPI schema:

```bash
make contract-test
```

Tests verify that all endpoints:
- Accept documented request formats
- Return documented response status codes
- Never crash with 5xx errors

**Load Testing (Locust)**

Test API performance under concurrent user load:

```bash
# Interactive mode (opens web UI at http://localhost:8089)
make load-test

# Headless CI mode (20 users, 60 seconds)
make load-test-headless
```

Load test scenarios are defined in [services/api/tests/load_tests/locustfile.py](services/api/tests/load_tests/locustfile.py). Uses realistic user workflows (expenses, reports, alerts) to identify performance bottlenecks.

### CI/CD & Automation

Single GitHub Actions pipeline for automated quality assurance:

**Full Pipeline (~8-10 min):**
- Triggered on every push and pull request
- Tests on Python 3.14
- Full unit + integration tests
- Type checking (mypy)
- Code quality (Ruff lint + Ruff format)
- Security scanning (bandit, pip-audit, TruffleHog)
- Pre-commit hooks validation
- API schema generation check
- Coverage reporting (Codecov)

Workflow file: `.github/workflows/ci-full.yml`

### Scripts Management

Administrative script in the `startup/` directory:

| Script | Purpose | Usage |
|--------|---------|-------|
| `project_spec.sh` | Admin bootstrap & DB init | `./startup/project_spec.sh` |

See [startup/](startup/) for the scripts.

## 📁 Project Structure
---

```
DEMO_FastAPI/
│
├── services/                       # Multi-service application architecture
│   ├── api/                        # FastAPI microservice (Python package: 'services.api')
│   │   ├── main.py                      # FastAPI application factory + exception handlers
│   │   ├── auth/                        # Authentication module (JWT router + schemas)
│   │   │   ├── router.py               # POST /token login endpoint
│   │   │   ├── schemas.py              # Token Pydantic schemas
│   │   │   └── service.py              # Auth business logic
│   │   │
│   │   ├── core/                        # Infrastructure & configuration
│   │   │   ├── config.py               # Pydantic Settings (environment config)
│   │   │   ├── security.py             # JWT, authentication, password hashing
│   │   │   ├── exceptions.py           # Custom exception classes
│   │   │   ├── enums.py                # UserRole, UserStatus, ExpenseCategory enums
│   │   │   ├── logging.py              # Logging configuration (file + console)
│   │   │   ├── middleware.py           # HTTP logging middleware
│   │   │   ├── metrics.py              # In-memory business metrics
│   │   │   ├── cache.py                # Cache utilities
│   │   │   └── branding.py             # Startup banner and log signature
│   │   │
│   │   ├── database/                    # Data layer
│   │   │   ├── base.py                 # Shared SQLAlchemy Base (Alembic-safe)
│   │   │   ├── session.py              # SQLAlchemy engine, sessionmaker, get_db(), run_migrations()
│   │   │   └── models/
│   │   │       ├── user.py             # User ORM model (id, username, budget, role, status)
│   │   │       └── expense.py          # Expense ORM model (id, amount, category, date)
│   │   │
│   │   ├── alembic/                    # Database migrations
│   │   │   ├── env.py                  # Alembic environment/bootstrap
│   │   │   └── versions/               # Revision files
│   │   │
│   │   ├── routers/                     # API endpoints (APIRouter pattern)
│   │   │   ├── auth.py                 # POST /token (login)
│   │   │   ├── users.py                # User CRUD + approval workflow endpoints
│   │   │   ├── expenses.py             # Expense CRUD endpoints
│   │   │   ├── alerts.py               # Budget alert endpoints
│   │   │   ├── reports.py              # Report generation endpoints
│   │   │   ├── analytics.py            # Analytics endpoints
│   │   │   └── health.py               # Liveness, readiness, startup checks
│   │   │
│   │   ├── services/                    # Business logic layer
│   │   │   ├── auth_service.py         # Authentication & token management
│   │   │   ├── user_service.py         # User CRUD & admin operations
│   │   │   ├── expense_service.py      # Expense management & filtering
│   │   │   ├── alert_service.py        # Budget alerts & threshold monitoring
│   │   │   └── report_service.py       # Analytics & reporting
│   │   │
│   │   ├── schemas/                     # Pydantic request/response models
│   │   │   ├── user.py                 # UserCreate, UserUpdate, UserResponse
│   │   │   ├── expense.py              # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   │   │   └── common.py               # Shared schemas
│   │   │
│   │   ├── utils/                       # Generic utilities
│   │   │   ├── dependencies.py         # get_admin_user(), get_current_user() dependencies
│   │   │   ├── print_banner.py         # Banner rendering helper
│   │   │   ├── static/
│   │   │   │   └── favicon.svg
│   │   │   └── branding/
│   │   │       ├── startup.txt
│   │   │       ├── completion.txt
│   │   │       ├── setup.txt
│   │   │       └── mammoth.txt
│   │   │
│   │   ├── logs/                        # Application logs (git-ignored)
│   │   │   ├── app.log                 # Text log file
│   │   │   ├── app.jsonl               # Structured JSONL logs
│   │   │   └── config/
│   │   │       └── logging.yaml        # Logging configuration
│   │   │
│   │   └── tests/                       # Automated test suite (pytest)
│   │       ├── conftest.py             # Pytest fixtures & configuration
│   │       ├── test_auth.py            # Authentication tests
│   │       ├── test_users.py           # User management tests
│   │       ├── test_expenses.py        # Expense CRUD tests
│   │       ├── test_alerts.py          # Alert tests
│   │       ├── test_reports.py         # Report tests
│   │       ├── test_security.py        # Security tests
│   │       ├── test_contract.py        # Schemathesis contract tests
│   │       └── load_tests/
│   │           └── locustfile.py       # Locust load test scenarios
│   │
│   ├── data/                           # SQLite database (git-ignored)
│   │   └── expense_tracker.db          # SQLite database (auto-created)
│
├── doc/                            # Project documentation
│   ├── DEVELOPMENT.md              # Development workflow, pre-commit, Makefile targets
│   ├── STANDARDS.md                # Code standards, naming conventions, type hints
│   └── RATE_LIMITING.md            # Rate limiting implementation details
│
├── startup/                        # Administrative bootstrap script
│   ├── project_spec.sh             # Admin bootstrap & database init
│
│
├── .github/                        # GitHub configuration
│   └── workflows/
│       └── ci-full.yml             # Full CI on each push and pull request
│
├── Root Configuration Files
│   ├── Makefile                    # Build, run, and deployment automation
│   ├── pyproject.toml              # Workspace root for uv (services are managed from here)
│   ├── uv.lock                     # Locked dependency versions (commit this)
│   ├── .pre-commit-config.yaml     # Pre-commit hooks configuration (13 checks)
│   ├── .python-version             # Python version pin for pyenv (3.14)
│   ├── .env.example                # Dev environment variables template
│   └── LICENSE                     # CC BY-NC 4.0

├── .env                            # Dev local (git-ignored, created by make init-env)
└── .gitignore                      # Git ignore rules
```

**Key Directories:**
- **`services/`** - Multi-service microservices architecture
  - **`services/api/`** - FastAPI service with its own `pyproject.toml` (code, tests, logs — self-contained)
- **`doc/`** - Specialized documentation (deployment, development, standards, rate limiting)
- **`startup/`** - Administrative bootstrap script (admin account initialization)

**Configuration & Deployment:**
- **`Makefile`** - Simplifies common development and dependency-management tasks
- **Root `pyproject.toml` + `uv.lock`** - Workspace orchestration and shared lockfile
- **`services/api/pyproject.toml`** - API service runtime dependencies only

## 📊 Data Structures
---

### Enums

Defined in `services/api/core/enums.py`, used throughout the application for type safety and validation:

**UserRole**
```python
class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
```

**UserStatus**
```python
class UserStatus(str, Enum):
    PENDING = "pending"      # Awaiting approval
    ACTIVE = "active"        # Can access API
    DISABLED = "disabled"    # Rejected or suspended
```

**ExpenseCategory**
```python
class ExpenseCategory(str, Enum):
    FOOD = "food"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    OTHER = "other"
```

### ORM Models & Database Schema

#### Technology Stack

- **Engine**: SQLite (file-based, no server required)
- **ORM**: SQLAlchemy 2.0.46
- **Schema management**: Alembic migrations applied automatically on app startup
- **Type Validation**: Pydantic + SQLAlchemy integration

#### Users Table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | STRING(36) | Primary Key | UUID |
| username | STRING | UNIQUE, NOT NULL | Login identifier |
| hashed_password | STRING | NOT NULL | Argon2 hashed |
| budget | NUMERIC(12,2) | NOT NULL | Monthly budget limit |
| role | ENUM(UserRole) | NOT NULL, default="user" | Values: admin, moderator, user |
| status | ENUM(UserStatus) | NOT NULL, default="pending" | Values: pending, active, disabled |

**ORM Model**: `services/api/database/models/user.py`

#### Expenses Table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | STRING(36) | Primary Key | UUID |
| description | STRING | NOT NULL | Expense description |
| amount | NUMERIC(12,2) | NOT NULL | Amount > 0 |
| date | DATETIME | NOT NULL | When incurred (default=now) |
| category | ENUM(ExpenseCategory) | NOT NULL | food, transportation, entertainment, utilities, healthcare, education, shopping, other |
| user_id | STRING(36) | Foreign Key → users.id | Expense owner |

**ORM Model**: `services/api/database/models/expense.py`

### API Request/Response Models

Defined in `services/api/schemas/`, these Pydantic models validate and serialize API requests/responses:

**User Operations**
- `UserCreate`: username, password (min 6 chars), budget (≥ 0, defaults to 0.0)
- `UserSelfUpdate`: username/password/budget only (extra fields forbidden)
- `UserUpdate`: admin update schema (username, password, budget, role, status)
- `UserResponse`: includes id, role, status

**Expense Operations**
- `ExpenseCreate`: description, amount (> 0), category enum
- `ExpenseUpdate`: all fields optional
- `ExpenseResponse`: includes id, datetime, user_id

### Managing the Database

Use [DBeaver Community Edition](https://dbeaver.io/) to browse and edit your SQLite database graphically.

⚠️ **Important**: Stop the API server before making manual database changes to avoid file locks.

### Database Migration

The application now uses **Alembic** for schema management.

```bash
# Apply all migrations to the configured database
make migrate

# Create a new revision after model changes
make migrate-create MSG="add new field"
```

The default local database can still be SQLite. For production at scale, consider PostgreSQL or MySQL:

```python
# services/api/core/config.py
# DATABASE_URL = "postgresql://user:password@localhost/expense_tracker"  # pragma: allowlist secret
```

The modular design allows easy database swaps with minimal code changes.

## 🔌 API Endpoints
---

### Role-Based Access Control

All endpoints have defined permission requirements:

- **🟢 PUBLIC**: No authentication required
- **🔵 USER**: Any authenticated user with `status=ACTIVE`
- **🟣 MODERATOR**: MODERATOR or ADMIN role
- **🔴 ADMIN**: ADMIN role only

### Authentication
- `POST /token` 🟢 – Login with username/password, returns JWT token

### User Management

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/users/create` | POST | 🟢 PUBLIC | Create new user account (starts with status: PENDING) |
| `/users/create-active` | POST | 🟢 PUBLIC | Create user with ACTIVE status (dev/test only) |
| `/users/me` | GET | 🔵 USER | Get authenticated user's profile |
| `/users/` | GET | 🔴 ADMIN | List all users (filterable by status: pending/active/disabled) |
| `/users/update/` | PUT | 🔵 USER | Update own profile (username, password, budget only) |
| `/users/update/{user_id}/` | PUT | 🔴 ADMIN | Update any user (role, status, all fields) |
| `/users/{user_id}/approve` | POST | 🟣🔴 MODERATOR+ADMIN | Approve PENDING user → ACTIVE |
| `/users/{user_id}/reject` | POST | 🟣🔴 MODERATOR+ADMIN | Reject PENDING user → DISABLED |
| `/users/{user_id}/disable` | POST | 🟣🔴 MODERATOR+ADMIN | Suspend ACTIVE user → DISABLED |
| `/users/{user_id}/reactivate` | POST | 🟣🔴 MODERATOR+ADMIN | Reactivate DISABLED user → ACTIVE |
| `/users/delete/{user_id}/` | DELETE | 🔴 ADMIN | Delete user (admins cannot delete themselves) |

### Expenses

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/expenses/` | GET | 🔵 USER | List authenticated user's expenses |
| `/expenses/` | POST | 🔵 USER | Add new expense |
| `/expenses/{expense_id}` | GET | 🔵 USER | Get one expense by ID (must own it) |
| `/expenses/{expense_id}` | PUT | 🔵 USER | Update expense (must own it) |
| `/expenses/{expense_id}` | DELETE | 🔵 USER | Delete expense (must own it) |

### Reports

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/reports/monthly/{year}/{month}` | GET | 🔵 USER | Monthly expense summary (authenticated user) |
| `/reports/period` | GET | 🔵 USER | Custom period report (authenticated user) |
| `/reports/all` | GET | 🔴 ADMIN | All users' reports (admin only) |

### Alerts

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/alerts/` | GET | 🔵 USER | Check for budget overruns |

### Analytics

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/analytics/` | GET | 🔴 ADMIN | Business KPIs snapshot (user counts, expense totals, in-memory counters) |

### Health

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/health/live` | GET | 🟢 PUBLIC | Process liveness check |
| `/health/ready` | GET | 🟢 PUBLIC | Readiness check (includes database ping) |
| `/health/startup` | GET | 🟢 PUBLIC | Startup phase completion check |
| `/health` | GET | 🟢 PUBLIC | Legacy alias for liveness |

## 🔐 Authentication & Authorization
---

### User Status Workflow

New users follow an approval workflow before they can access the API:

```
1. User Registration (POST /users/create)
   ↓
   Status: PENDING ❌ (cannot login)
   ↓
2. Admin/Moderator Reviews
   ↓
  ├─→ POST /users/{id}/approve → Status: ACTIVE ✅ (can login)
   └─→ POST /users/{id}/reject  → Status: DISABLED ❌ (approved= false)
   ↓
3. Active User Lifecycle
   ↓
  ├─→ POST /users/{id}/disable    → Status: DISABLED ❌ (suspended from management)
   └─→ POST /users/{id}/reactivate → Status: ACTIVE ✅ (restored)
```

### Role Hierarchy

| Role | Permissions | Can... |
|------|-------------|--------|
| **USER** | Basic access | Manage own expenses, view own reports, set budget |
| **MODERATOR** | User validation | Approve/reject/disable/reactivate users |
| **ADMIN** | Full system | All MODERATOR actions + user CRUD + system reports |

### Access Control Details

- **Method**: OAuth2 with JWT (Bearer tokens)
- **Token Expiration**: Configurable via `JWT_EXPIRATION_MINUTES` (.env)
- **Password Hashing**: Argon2 via pwdlib
- **Required Status**: Only users with `status=ACTIVE` can authenticate
- **Ownership**: Non-admin users can only access their own data (expenses, profile)

## ⚠️ Exception Handling
---

Custom exceptions with proper HTTP status codes:

| Exception | Status | Use Case |
|-----------|--------|----------|
| `AppException` | 400 | Generic application errors |
| `ValidationException` | 422 | Request validation failures |
| `AuthenticationException` | 401 | Invalid credentials |
| `AuthorizationException` | 403 | Insufficient permissions |
| `ResourceNotFoundException` | 404 | Resource doesn't exist |
| `ConflictException` | 409 | Resource conflict (duplicate) |
| `InternalServerException` | 500 | Server errors |

All exceptions are caught by global exception handlers in `services/api/main.py` and return JSON responses.

---

## 🛠️ Code Quality & Development Standards
---

This project maintains strict code quality standards enforced through pre-commit hooks (10+ checks), type hints, Google-style docstrings, and Makefile automation.

**For details:**
- **[doc/STANDARDS.md](doc/STANDARDS.md)** — Code conventions, naming, docstrings, type hints
- **[doc/DEVELOPMENT.md](doc/DEVELOPMENT.md)** — Development workflow, pre-commit setup, Makefile targets

---

## 📖 Extra documentation

For specialized topics and detailed guides:

| Document | Purpose |
|----------|----------|
| **[doc/RATE_LIMITING.md](doc/RATE_LIMITING.md)** | Rate limiting implementation with slowapi + Redis |
| **[doc/DEVELOPMENT.md](doc/DEVELOPMENT.md)** | Development setup, pre-commit hooks, code quality workflow |
| **[doc/STANDARDS.md](doc/STANDARDS.md)** | Code standards, naming conventions, docstring format, type hints |

## 📚 Resources
---

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [pwdlib Documentation](https://frankie567.github.io/pwdlib/)
- [DBeaver Database Tool](https://dbeaver.io/)

## 🤝 Contributing
---

Contributions are welcome! For detailed guidelines on how to contribute, including:
- Development setup and environment
- Code quality standards and style guides
- Pre-commit hooks and testing requirements
- Commit message guidelines and PR process

Please see [**CONTRIBUTING.md**](CONTRIBUTING.md) for complete instructions.

## 💬 Support
---

> Maintained by [Hag-Zilla](https://github.com/Hag-Zilla)

## 📜 License
---

See [LICENSE](LICENSE) file for details.
