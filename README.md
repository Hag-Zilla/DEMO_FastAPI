<div align="center">

# Personal Expense Tracking API

A production-ready FastAPI demo showcasing a complete REST API for expense management with authentication, budgeting, and reporting.

**Built with:** FastAPI • SQLAlchemy • Pydantic • SQLite

</div>

![Python](https://img.shields.io/badge/python-3.14-blue.svg) ![FastAPI](https://img.shields.io/badge/framework-FastAPI-green.svg) ![Docker](https://img.shields.io/badge/docker-✓-blue.svg) ![Makefile](https://img.shields.io/badge/Makefile-✓-orange.svg) [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/Hag-Zilla/DEMO_FastAPI)](https://github.com/Hag-Zilla/DEMO_FastAPI/releases) [![CI](https://github.com/Hag-Zilla/DEMO_FastAPI/actions/workflows/ci.yml/badge.svg)](https://github.com/Hag-Zilla/DEMO_FastAPI/actions) [![codecov](https://img.shields.io/codecov/c/gh/Hag-Zilla/DEMO_FastAPI.svg)](https://codecov.io/gh/Hag-Zilla/DEMO_FastAPI)

## Table of Contents

- [About](#about)
- [Features](#features)
- [Quick Start](#quick-start)
  - [Clone and Setup Environment](#clone-and-setup-environment)
    - [Essential Configuration Variables](#essential-configuration-variables)
    - [Build and Run Services](#build-and-run-services)
    - [Verify Installation](#verify-installation)
  - [Advanced Workflows](#advanced-workflows)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Logging](#logging)
- [Project Structure](#project-structure)
- [Data Structures](#data-structures)
  - [Enums](#enums)
  - [ORM Models & Database Schema](#orm-models--database-schema)
  - [Technology Stack](#technology-stack)
  - [API Request/Response Models](#api-requestresponse-models)
  - [Managing the Database](#managing-the-database)
  - [Database Migration](#database-migration)
- [API Endpoints](#api-endpoints)
  - [Role-Based Access Control](#role-based-access-control)
  - [Authentication](#authentication)
  - [User Management](#user-management)
  - [Expenses](#expenses)
  - [Reports](#reports)
  - [Alerts](#alerts)
  - [Health](#health)
- [Authentication & Authorization](#authentication--authorization)
  - [User Status Workflow](#user-status-workflow)
  - [Role Hierarchy](#role-hierarchy)
  - [Access Control Details](#access-control-details)
  - [Example Authentication Flow](#example-authentication-flow)
- [Exception Handling](#exception-handling)
- [Testing](#testing)
- [Make commands list](#make-commands-list)
- [Resources](#resources)
- [Extra documentation](#extra-documentation)
  - [doc/DEPLOYMENT.md](doc/DEPLOYMENT.md)
  - [doc/RATE_LIMITING.md](doc/RATE_LIMITING.md)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## About
---

A personal expense tracking API built with **FastAPI** and **SQLite**. Users can manage their expenses, set monthly budgets, receive alerts for budget overruns, and generate detailed expense reports. The project demonstrates best practices in API design, authentication, database modeling, and production-ready application structure.

## Features
---

- **User Management**: Create accounts, OAuth2 authentication, role-based access control (admin/moderator/user)
- **User Approval Workflow**: Admin/Moderator review and approval of new user registrations (pending/active/disabled statuses)
- **Expense Tracking**: Add, update, delete expenses with typed categories and datetime tracking
- **Budget Management**: Set personal budgets with automatic tracking
- **Alerts**: Real-time detection of budget overruns
- **Reports**: Generate monthly and custom-period expense reports by category
- **Admin & Moderator Interface**: System-wide user and expense management with moderation capabilities
- **DDoS Protection**: 4-layer defense system (firewall, reverse proxy, application-level rate limiting, distributed quota storage)
- **Rate Limiting**: Distributed request rate limiting with slowapi and Redis
- **Error Handling**: Custom exception classes with proper HTTP status codes
- **Logging**: Console and file-based logging for monitoring
- **Type Validation**: Pydantic v2 with enums for categories and roles

## Quick Start
---

### Clone and Setup Environment

```bash
git clone <repo-url>
cd DEMO_FastAPI
make init-env    # Create .env files from templates
```

### Essential Configuration Variables

Edit `.env` and set these required values:

```bash
nano .env
```

**Essential variables:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | JWT signing key (min 32 chars) | `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Token expiration | `30` |
| `DATABASE_URL` | SQLite database path | `sqlite:///./data/expense_tracker.db` |
| `DEBUG` | Debug mode (⚠️ `False` in production) | `True` (dev), `False` (prod) |

Quick generation:
```bash
# Generate SECRET_KEY
ossl rand -hex 32

# For Docker, also set REDIS_PASSWORD
openssl rand -hex 16
```

> **For Docker development and production**, see [doc/DEPLOYMENT.md](doc/DEPLOYMENT.md#environment-configuration) for environment-specific configuration files (`.env.docker.dev`, `.env.docker.prod`) and detailed setup instructions.

### Build and Run Services

**For local development:**

```bash
# Install dependencies (uses committed uv.lock or requirements.txt)
make init

# Activate virtual environment
source .venv/bin/activate  # or ./venv/bin/activate

# Start the API
make run
```

For **Docker development** and **Docker production** setup, see [Build and Run Services](doc/DEPLOYMENT.md#build-and-run-services) in the deployment guide.

### Verify Installation

**Check if services are running:**

```bash
# Local development
curl http://localhost:8000/health

# Docker
docker-compose ps
curl http://localhost/health
```

**Access the API:**

- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Checks**:
  - Liveness: http://localhost:8000/health/live
  - Readiness: http://localhost:8000/health/ready
  - Startup: http://localhost:8000/health/startup

**Example request:**

```bash
curl -X POST "http://localhost:8000/users/create" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secure123", "budget": 1000}'
```


### Advanced Workflows

#### Contributor (use committed lock)

If `uv.lock` or `requirements.txt` is committed:

```bash
make init        # Install exact versions from lock
make test
make run
```

#### Maintainer (update dependencies)

To update dependencies and produce new lock:

```bash
# Update pyproject.toml as needed
make lock                 # generates/refreshes uv.lock
make export-reqs          # export pinned requirements.txt from uv.lock
git add pyproject.toml uv.lock requirements.txt
git commit -m "Update deps: refresh uv.lock and requirements.txt"
git push
```

**Notes:**
- If `uv.lock` is committed, contributors do NOT need to run `make lock`
- If `requirements.txt` is present, venv users can install directly without uv
- Generate lock on CI or platform matching production: `uv lock --python 3.14`

### Configuration

#### Environment Variables

Environment variables & secrets

| File | Purpose |
|------|---------|
| `.env` | Dev local (FastAPI only) |
| `.env.docker.dev` | Dev Docker (full stack) |
| `.env.docker.prod` | Production |

Settings are loaded via **Pydantic Settings** (`app/core/config.py`) with validation at startup.

- `DATABASE_URL` is the single source of truth for database connection.
- For SQLite, the app auto-creates the parent folder (default: `data/`).
- `setup.sh` does not overwrite `DATABASE_URL`; your `.env` value is preserved.

For detailed setup of `.env.docker.dev` and `.env.docker.prod`, see [Configuration in doc/DEPLOYMENT.md](doc/DEPLOYMENT.md#configuration).

#### Logging

Logs are written to:
- **Console**: For development feedback
- **File**: `logs/app.log` for production monitoring

Configured via YAML in `logs/config/logging.yaml`, loaded by `app/core/logging.py`.

For production logging configuration, monitoring setup, and log aggregation, see [Monitoring & Health Checks in doc/DEPLOYMENT.md](doc/DEPLOYMENT.md#monitoring).

## Project Structure
---

```
DEMO_FastAPI/
│
├── app/                         # Main application package
│   ├── main.py                      # FastAPI application factory + exception handlers
│   │
│   ├── core/                        # Infrastructure & configuration
│   │   ├── config.py               # Pydantic Settings (environment config)
│   │   ├── security.py             # JWT, authentication, password hashing
│   │   ├── exceptions.py           # Custom exception classes
│   │   ├── enums.py                # UserRole, UserStatus, ExpenseCategory enums
│   │   ├── logging.py              # Logging configuration (file + console)
│   │   ├── middleware.py           # HTTP logging middleware
│   │   └── branding.py             # Startup banner and log signature
│   │
│   ├── database/                    # Data layer
│   │   ├── session.py              # SQLAlchemy engine, sessionmaker, get_db()
│   │   └── models/
│   │       ├── user.py             # User ORM model (id, username, budget, role, status)
│   │       └── expense.py          # Expense ORM model (id, amount, category, date)
│   │
│   ├── routers/                     # API endpoints (APIRouter pattern)
│   │   ├── auth.py                 # POST /token (login)
│   │   ├── users.py                # User CRUD + approval workflow endpoints
│   │   ├── expenses.py             # Expense CRUD endpoints
│   │   ├── alerts.py               # Budget alert endpoints
│   │   ├── reports.py              # Report generation endpoints
│   │   └── health.py               # Liveness, readiness, startup checks
│   │
│   ├── schemas/                     # Pydantic request/response models
│   │   ├── user.py                 # UserCreate, UserUpdate, UserResponse
│   │   ├── expense.py              # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   │   └── common.py               # Token schema
│   │
│   └── utils/                       # Generic utilities
│       ├── dependencies.py          # get_admin_user(), get_current_user() dependencies
│       ├── print_banner.py          # Banner rendering helper
│       ├── static/
│       │   └── favicon.svg
│       └── branding/
│           ├── startup.txt
│           ├── completion.txt
│           ├── setup.txt
│           └── mammoth.txt
│
├── doc/                            # Project documentation
│   ├── DEPLOYMENT.md               # Production deployment, firewall, monitoring, scaling
│   └── RATE_LIMITING.md            # Rate limiting implementation details
│
├── nginx/                          # Reverse proxy configuration (Docker production)
│   └── nginx.conf                  # Nginx config: SSL, rate limiting, routing
│
├── logs/                           # Log output directory
│   ├── app.log                     # Application log file
│   ├── app.jsonl                   # Structured JSONL logs
│   └── config/
│       └── logging.yaml            # Logging configuration
│
├── data/                           # SQLite database directory
│   └── expense_tracker.db          # SQLite database (auto-created)
│
├── Root Configuration Files
│   ├── docker-compose.yml          # Multi-service orchestration (FastAPI, Nginx, Redis)
│   ├── firewall-rules.sh           # Bash script for host firewall setup (ufw/nftables)
│   ├── Makefile                    # Build, run, and deployment automation
│   ├── pyproject.toml              # uv project config + dependency constraints
│   ├── requirements.txt            # Python dependencies (exported from uv.lock)
│   ├── uv.lock                     # Locked dependency versions (commit this)
│   ├── setup.sh                    # Initial setup script
│   ├── .env.example                # Dev environment variables template
│   ├── .env.docker.dev.example     # Docker dev environment template
│   ├── .env.docker.prod.example    # Docker production environment template
│   └── LICENSE                     # CC BY-NC 4.0

├── .env                            # Dev local (git-ignored, created by make init-env)
├── .env.docker.dev                 # Docker dev (git-ignored, created by make init-env)
├── .env.docker.prod                # Docker prod (git-ignored, created by make init-env)
└── .gitignore                      # Git ignore rules
```

**Key Directories:**
- **`app/`** - FastAPI application (authentication, endpoints, data models)
- **`doc/`** - Specialized documentation (deployment, rate limiting)
- **`nginx/`** - Docker production reverse proxy configuration
- **`logs/`** - Application logs (JSON and text formats)
- **`data/`** - SQLite database location

**Configuration & Deployment:**
- **`docker-compose.yml`** - Orchestrates FastAPI, Nginx, Redis containers
- **`firewall-rules.sh`** - **MUST run before docker-compose** for DDoS protection
- **`Makefile`** - Simplifies common development and deployment tasks
- **`pyproject.toml` + `uv.lock`** - Pinned dependency management

For Docker deployment details and firewall setup, see [Build and Run Services in doc/DEPLOYMENT.md](doc/DEPLOYMENT.md#build-and-run-services).

## Data Structures
---

### Enums

Defined in `app/core/enums.py`, used throughout the application for type safety and validation:

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
- **Auto-creation**: Tables created automatically on app startup
- **Type Validation**: Pydantic + SQLAlchemy integration

#### Users Table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Primary Key | Auto-increment |
| username | STRING | UNIQUE, NOT NULL | Login identifier |
| hashed_password | STRING | NOT NULL | Argon2 hashed |
| budget | FLOAT | NOT NULL | Monthly budget limit |
| role | ENUM(UserRole) | NOT NULL, default="user" | Values: admin, moderator, user |
| status | ENUM(UserStatus) | NOT NULL, default="pending" | Values: pending, active, disabled |
| disabled | BOOLEAN | default=False | Legacy account status field |

**ORM Model**: `app/database/models/user.py`

#### Expenses Table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Primary Key | Auto-increment |
| description | STRING | NOT NULL | Expense description |
| amount | FLOAT | NOT NULL | Amount > 0 |
| date | DATETIME | NOT NULL | When incurred (default=now) |
| category | ENUM(ExpenseCategory) | NOT NULL | food, transportation, entertainment, utilities, healthcare, education, shopping, other |
| user_id | INTEGER | Foreign Key → users.id | Expense owner |

**ORM Model**: `app/database/models/expense.py`

### API Request/Response Models

Defined in `app/schemas/`, these Pydantic models validate and serialize API requests/responses:

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

SQLite works fine for small deployments. For production at scale, consider PostgreSQL or MySQL:

```python
# app/core/config.py
# DATABASE_URL = "postgresql://user:password@localhost/expense_tracker"
```

The modular design allows easy database swaps with minimal code changes.

## API Endpoints
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

### Health

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/health/live` | GET | 🟢 PUBLIC | Process liveness check |
| `/health/ready` | GET | 🟢 PUBLIC | Readiness check (includes database ping) |
| `/health/startup` | GET | 🟢 PUBLIC | Startup phase completion check |
| `/health` | GET | 🟢 PUBLIC | Legacy alias for liveness |

## Authentication & Authorization
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
- **Password Hashing**: Argon2 via passlib
- **Required Status**: Only users with `status=ACTIVE` can authenticate
- **Ownership**: Non-admin users can only access their own data (expenses, profile)

### Example Authentication Flow

```bash
# 1. Create new user (PUBLIC)
curl -X POST "http://localhost:8000/users/create" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secure123", "budget": 1000}'
# Response: {..., "status": "pending"}

# 2. Try login with PENDING status (FAILS - 403)
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secure123&grant_type=password"
# Response: 403 "User account is not active"

# 3. Admin/Moderator approves user (MODERATOR role)
curl -X POST "http://localhost:8000/users/1/approve" \
  -H "Authorization: Bearer ADMIN_TOKEN"
# Response: {..., "status": "active"}

# 4. Now user can login (ACTIVE status)
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secure123&grant_type=password"
# Response: {"access_token": "eyJhbGc...", "token_type": "bearer"}

# 5. Use token in requests
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGc..."
```

## Exception Handling
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

All exceptions are caught by global exception handlers in `app/main.py` and return JSON responses.

## Testing
---

Run the interactive API documentation to test endpoints:

```bash
# After starting the server, visit:
http://localhost:8000/docs
```

Or use curl:

```bash
# Create user
curl -X POST "http://localhost:8000/users/create" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secure123", "budget": 1000}'

# Get current user
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Make commands list
---

The project provides a `Makefile` to simplify common workflows for both development and production:

**Development (Local without Docker):**
```bash
make init-env        # create .env files from templates
make init            # interactive setup (default: uv)
make init-uv         # setup with uv (non-interactive)
make init-venv       # setup with venv/pip (non-interactive)
make sync            # install/sync dependencies from uv.lock
make run             # run FastAPI dev server (auto-reload)
make test            # run pytest suite
make lint            # run flake8 linting on app/
make format          # format code with black
```

**Dependency Management:**
```bash
make lock            # refresh uv lockfile
make export-reqs     # export pinned requirements.txt from uv.lock (for venv users)
```

**Docker (Production):**
```bash
make docker-build    # build Docker images
make docker-up       # start containers (docker-compose up -d)
make docker-down     # stop containers (docker-compose down)
make docker-logs     # view container logs (follow mode)
make docker-test     # run tests inside app container
make docker-clean    # cleanup Docker artifacts
make docker-shell    # open bash shell in app container
```

**Maintenance:**
```bash
make bootstrap-admin # bootstrap admin user (interactive)
make clean           # remove Python cache files
make help            # show all available targets
make clean           # remove common cache/build artifacts
```


## Resources
---

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [Passlib Hashing](https://passlib.readthedocs.io/)
- [DBeaver Database Tool](https://dbeaver.io/)

##  Extra documentation

For specialized topics:

| Document | Purpose |
|----------|----------|
| **[doc/DEPLOYMENT.md](doc/DEPLOYMENT.md)** | Production deployment, scaling, monitoring, troubleshooting |
| **[doc/RATE_LIMITING.md](doc/RATE_LIMITING.md)** | Rate limiting implementation with slowapi + Redis |

## Contributing
---

Contributions are welcome! If you have scripts, tools, or improvements to share:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-tool`)
3. Commit your changes (`git commit -m 'Add some amazing tool'`)
4. Push to the branch (`git push origin feature/amazing-tool`)
5. Open a Pull Request

Please ensure your scripts include:
- Clear documentation
- Error handling
- Usage instructions
- Comments in English


## Support
---

> Maintained by [Hag-Zilla](https://github.com/Hag-Zilla)

## License
---

See [LICENSE](LICENSE) file for details.
