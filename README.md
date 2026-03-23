<div align="center">

# Personal Expense Tracking API

A production-ready FastAPI demo showcasing a complete REST API for expense management with authentication, budgeting, and reporting.

**Built with:** FastAPI • SQLAlchemy • Pydantic • SQLite

</div>

![Python](https://img.shields.io/badge/python-3.14-blue.svg) ![FastAPI](https://img.shields.io/badge/framework-FastAPI-green.svg) ![Docker](https://img.shields.io/badge/docker-✓-blue.svg) ![Makefile](https://img.shields.io/badge/Makefile-✓-orange.svg) [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/Hag-Zilla/DEMO_FastAPI)](https://github.com/Hag-Zilla/DEMO_FastAPI/releases) [![CI](https://github.com/Hag-Zilla/DEMO_FastAPI/actions/workflows/ci.yml/badge.svg)](https://github.com/Hag-Zilla/DEMO_FastAPI/actions) [![codecov](https://img.shields.io/codecov/c/gh/Hag-Zilla/DEMO_FastAPI.svg)](https://codecov.io/gh/Hag-Zilla/DEMO_FastAPI)

## 📖 Table of Contents

- [📋 About](#-about)
- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📚 Documentation](#-documentation)
- [🌐 Access the API](#-access-the-api)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🗄️ Database](#-database)
- [🔌 API Endpoints](#-api-endpoints)
- [🔐 Authentication & Authorization](#-authentication--authorization)
- [🛡️ Exception Handling](#️-exception-handling)
- [📊 Data Structures](#-data-structures)
- [🧪 Testing](#-testing)
- [🚢 Deployment Notes](#-deployment-notes)
- [📚 Resources](#-resources)
- [🤝 Contributing](#-contributing)
- [💬 Support](#-support)
- [📝 License](#-license)

---

## 📋 About
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
- **DDoS Protection**: 4-layer defense system (firewall, reverse proxy, application-level rate limiting, distributed quota storage)
- **Rate Limiting**: Distributed request rate limiting with slowapi and Redis
- **Error Handling**: Custom exception classes with proper HTTP status codes
- **Logging**: Console and file-based logging for monitoring
- **Type Validation**: Pydantic v2 with enums for categories and roles

## 🚀 Quick Start
---

Two simple flows are supported: one for typical contributors (who consume the repo), and one for maintainers (who change dependencies).

### Contributor (quick start — use committed lock)


1) Clone and prepare environment

```bash
git clone <repo-url>
cd DEMO_FastAPI
make init-env    # Create .env files from templates (.env, .env.docker.dev, .env.docker.prod)
nano .env        # Edit with your values
nano .env.docker.dev        # Edit with your values
nano .env.docker.prod       # Edit with your values
```

Tips :

```bash
# Generate SECRET_KEY (min 32 chars)
openssl rand -hex 32

# Generate REDIS_PASSWORD
openssl rand -hex 16
```


2) Initialize environment (uses committed `uv.lock` / `requirements.txt` if present)

```bash
# Interactive (defaults to uv)
make init
# or force paths:
make init-uv    # use uv
make init-venv  # use venv (uses requirements.txt if present)
```

3) Run tests and start

```bash
make test
source .venv/bin/activate  # or ./venv/bin/activate
make run # It will start the API
```

### Maintainer (update dependencies — produce canonical lock)

1) If you change `pyproject.toml` or need to update dependency versions, maintainers should produce and commit the canonical lock and an exported `requirements.txt` for venv users:

```bash
# update pyproject.toml as needed
make lock                 # generates/refreshes uv.lock
make export-reqs          # export pinned requirements.txt from uv.lock
git add pyproject.toml uv.lock requirements.txt
git commit -m "Update deps: refresh uv.lock and exported requirements.txt"
git push
```

Notes
- If `uv.lock` is committed, contributors do NOT need to run `make lock` — `uv sync` (used by `make init`) will install the exact versions from the lock.
- If `requirements.txt` is present, `venv` users can install from it directly without `uv`.
- To ensure the lock matches production, generate `uv.lock` on the CI or the platform matching production (use `uv lock --python 3.14` to target a specific Python minor).

This split keeps onboarding minimal for contributors, while allowing maintainers to control the canonical dependency graph for CI/production.

2) Run tests and start

```bash
make test
source .venv/bin/activate  # or ./venv/bin/activate
make run # It will start the API
```

### Access the API

- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Liveness Check**: http://localhost:8000/health/live
- **Readiness Check**: http://localhost:8000/health/ready
- **Startup Check**: http://localhost:8000/health/startup
- **Legacy Health Check**: http://localhost:8000/health

## 📁 Project Structure
---

```
app/
├── main.py                      # FastAPI application factory + exception handlers
│
├── core/                        # Infrastructure & configuration
│   ├── config.py               # Pydantic Settings (environment config)
│   ├── security.py             # JWT, authentication, password hashing
│   ├── exceptions.py           # Custom exception classes
│   ├── enums.py                # UserRole, ExpenseCategory enums
│   ├── logging.py              # Logging configuration (file + console)
│   ├── middleware.py           # HTTP logging middleware
│   └── branding.py             # Startup banner and log signature
│
├── database/                    # Data layer (Recettes vs Ustensiles)
│   ├── session.py              # SQLAlchemy engine, sessionmaker, get_db()
│   └── models/
│       ├── user.py             # User ORM model (id, username, budget, role)
│       └── expense.py          # Expense ORM model (id, amount, category, date)
│
├── routers/                     # API endpoints (APIRouter pattern)
│   ├── auth.py                 # POST /token (login)
│   ├── users.py                # User CRUD endpoints
│   ├── expenses.py             # Expense endpoints
│   ├── alerts.py               # Budget alert endpoints
│   ├── reports.py              # Report generation
│   └── health.py               # Liveness and readiness checks
│
├── schemas/                     # Pydantic request/response models
│   ├── user.py                 # UserCreate, UserUpdate, UserResponse
│   ├── expense.py              # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   └── common.py               # Token schema
│
└── utils/                       # Generic utilities (Ustensiles)
  ├── dependencies.py         # get_admin_user() dependency
  ├── print_banner.py         # Banner rendering helper
  ├── static/
  │   └── favicon.svg
  └── branding/
    ├── startup.txt
    ├── completion.txt
    ├── setup.txt
    └── mammoth.txt

Configuration Files:
├── .env.example                # Environment variables template
├── pyproject.toml              # Project metadata and dependency constraints (uv-first)
├── requirements.txt            # Python dependencies
└── setup.sh                    # Setup script

Logs:
├── logs/app.log                # Application log file
├── logs/app.jsonl              # Structured JSONL logs
└── logs/config/logging.yaml    # Logging configuration
```

## ⚙️ Configuration
---

### Environment Variables (`.env`)

Environment variables & secrets


| File | Purpose |
|------|---------|
| `.env` | Dev local (FastAPI only) |
| `.env.docker.dev` | Dev Docker (full stack) |
| `.env.docker.prod` | Production |


```env
# JWT Configuration
SECRET_KEY=your_super_secret_key_here_change_in_production
ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30

# Database Configuration
DATABASE_URL=sqlite:///./data/expense_tracker.db

# Application Configuration
APP_NAME=Expense Tracker API
APP_VERSION=1.0.0
DEBUG=False
```

Settings are loaded via **Pydantic Settings** (`app/core/config.py`) with validation at startup.

- `DATABASE_URL` is the single source of truth for database connection.
- For SQLite, the app auto-creates the parent folder (default: `data/`).
- `setup.sh` does not overwrite `DATABASE_URL`; your `.env` value is preserved.

### Logging

Logs are written to:
- **Console**: For development feedback
- **File**: `logs/app.log` for production monitoring

Configured via YAML in `logs/config/logging.yaml`, loaded by `app/core/logging.py`.

## 🗄️ Database
---

### Technology Stack

- **Engine**: SQLite (file-based, no server required)
- **ORM**: SQLAlchemy 2.0.46
- **Auto-creation**: Tables created automatically on app startup
- **Type Validation**: Pydantic models with SQLAlchemy mapped classes

### Database Schema

**Users Table**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Primary Key | Auto-increment |
| username | STRING | UNIQUE, NOT NULL | Login identifier |
| hashed_password | STRING | NOT NULL | Argon2 hashed |
| budget | FLOAT | NOT NULL | Monthly budget limit |
| role | ENUM(UserRole) | NOT NULL, default="user" | Values: admin, user |
| disabled | BOOLEAN | default=False | Account status |

**Expenses Table**

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | INTEGER | Primary Key | Auto-increment |
| description | STRING | NOT NULL | Expense description |
| amount | FLOAT | NOT NULL | Amount > 0 |
| date | DATETIME | NOT NULL | When incurred (default=now) |
| category | ENUM(ExpenseCategory) | NOT NULL | food, transportation, entertainment, utilities, healthcare, education, shopping, other |
| user_id | INTEGER | Foreign Key → users.id | Expense owner |

### Managing the Database

Use [DBeaver Community Edition](https://dbeaver.io/) to browse and edit your SQLite database graphically.

⚠️ **Important**: Stop the API server before making manual database changes to avoid file locks.

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

## 🛡️ Exception Handling
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

## 📊 Data Structures
---

### Enums

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

### Request/Response Models

**User Operations**
- `UserCreate`: username, password (min 6 chars), budget (≥ 0, defaults to 0.0)
- `UserSelfUpdate`: username/password/budget only (extra fields forbidden)
- `UserUpdate`: admin update schema (username, password, budget, role, status)
- `UserResponse`: includes id, role, status

**Expense Operations**
- `ExpenseCreate`: description, amount (> 0), category enum
- `ExpenseUpdate`: all fields optional
- `ExpenseResponse`: includes id, datetime, user_id


## 🧪 Testing
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

## 🚢 Deployment Notes
---

### Development

```bash
uvicorn app.main:app --reload
```

### Production

```bash
# Use Gunicorn with Uvicorn workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Database Migration

SQLite works fine for small deployments. For production at scale, consider PostgreSQL or MySQL:

```python
# app/core/config.py
# DATABASE_URL = "postgresql://user:password@localhost/expense_tracker"
```

The modular design allows easy database swaps with minimal code changes.

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


## 📚 Resources
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

## 🤝 Contributing
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


## 💬 Support
---

> Maintained by [Hag-Zilla](https://github.com/Hag-Zilla)

## 📝 License
---

See [LICENSE](LICENSE) file for details.
