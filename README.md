<div align="center">

# Personal Expense Tracking API

A production-ready FastAPI demo showcasing a complete REST API for expense management with authentication, budgeting, and reporting.

**Built with:** FastAPI • SQLAlchemy • Pydantic • SQLite

</div>

## 📋 About
---

A personal expense tracking API built with **FastAPI** and **SQLite**. Users can manage their expenses, set monthly budgets, receive alerts for budget overruns, and generate detailed expense reports. The project demonstrates best practices in API design, authentication, database modeling, and production-ready application structure.

## ✨ Features
---

- **User Management**: Create accounts, OAuth2 authentication, role-based access control (admin/user)
- **Expense Tracking**: Add, update, delete expenses with typed categories and datetime tracking
- **Budget Management**: Set personal budgets with automatic tracking
- **Alerts**: Real-time detection of budget overruns
- **Reports**: Generate monthly and custom-period expense reports by category
- **Admin Interface**: System-wide user and expense management
- **Error Handling**: Custom exception classes with proper HTTP status codes
- **Logging**: Console and file-based logging for monitoring
- **Type Validation**: Pydantic v2 with enums for categories and roles

## 🚀 Quick Start
---

### Prerequisites

- Python 3.11+
- `venv` or `uv`

### Setup Environment

```bash
bash setup.sh
```

The script guides you through environment setup (`venv` or `uv`), installs dependencies, and runs one-time admin bootstrap.

### Create `.env` File

Copy the example and adjust settings:

```bash
cp .env.example .env
```

### Admin Bootstrap (One-Shot)

During `setup.sh`, `project_spec.sh` is executed to create the initial `admin` user.

- The bootstrap runs only once and writes a lock file: `.admin_bootstrap_done`
- If you re-run setup later, admin bootstrap is skipped automatically
- If `admin` already exists and you force rerun, explicit confirmation is required
- Admin secret policy: min 12 chars, uppercase, lowercase, digit, special char
- To force a manual rerun:

```bash
ADMIN_BOOTSTRAP_FORCE=1 bash project_spec.sh
```

⚠️ Security note: the admin secret is not persisted in `.env`.
⚠️ Dependency note: Argon2 backend is installed via `requirements.txt` (`argon2-cffi`), not at bootstrap runtime.

### Run the API

```bash
# Activate environment
source ./venv/bin/activate  # or: source ./.venv/bin/activate (uv option)

# Start the server
uvicorn app.main:app --reload
```

**API is running at**: http://localhost:8000

## 🌐 Access the API
---

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
│   └── logging.py              # Logging configuration (file + console)
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
│   ├── expenses.py             # Expense endpoints (stub)
│   ├── alerts.py               # Budget alert endpoints (stub)
│   ├── reports.py              # Report generation (stub)
│   └── health.py               # Liveness and readiness checks
│
├── schemas/                     # Pydantic request/response models
│   ├── user.py                 # UserCreate, UserUpdate, UserResponse
│   ├── expense.py              # ExpenseCreate, ExpenseUpdate, ExpenseResponse
│   └── common.py               # Token schema
│
└── utils/                       # Generic utilities (Ustensiles)
    └── dependencies.py         # get_admin_user() dependency

Configuration Files:
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── environment.yml             # Project setup hints (name + Python version)
└── setup.sh                    # Setup script
```

## ⚙️ Configuration
---

### Environment Variables (`.env`)

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

### Authentication
- `POST /token` – Login with username/password, returns JWT token

### User Management
- `POST /users/create` – Create new standard user account (status: 201)
- `GET /users/me` – Get authenticated user's profile
- `PUT /users/update/` – Update authenticated user's profile (allowed fields: username, password, budget)
- `PUT /users/update/{user_id}/` – Admin: update any user (including role, disabled)
- `DELETE /users/delete/{user_id}/` – Admin: delete user (status: 204)

### Expenses
- `GET /expenses/` – List authenticated user's expenses
- `POST /expenses/` – Add new expense
- `GET /expenses/{expense_id}` – Get one expense by ID
- `PUT /expenses/{expense_id}` – Update expense
- `DELETE /expenses/{expense_id}` – Delete expense

### Reports
- `GET /reports/monthly/{year}/{month}` – Monthly expense summary
- `GET /reports/period` – Custom period report
- `GET /reports/all` – Admin: all users' reports

### Alerts
- `GET /alerts/` – Check for budget overruns

### Health
- `GET /health/live` – Process liveness check
- `GET /health/ready` – Readiness check (includes database ping)
- `GET /health/startup` – Startup phase completion check
- `GET /health` – Legacy alias for liveness

## 🔐 Authentication & Authorization
---

- **Method**: OAuth2 with JWT (Bearer tokens)
- **Token Expiration**: Configurable (`JWT_EXPIRATION_MINUTES`)
- **Password Hashing**: Argon2 via passlib
- **Role-based Access**: `@dependency` get_admin_user() for protected endpoints

### Example Authentication Flow

```bash
# 1. Login
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john_doe&password=secure_password123"

# Response:
# {"access_token": "eyJhbGc...", "token_type": "bearer"}

# 2. Use token in requests
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
    USER = "user"
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
- `UserUpdate`: admin update schema (username, password, budget, role, disabled)
- `UserResponse`: includes id, role, disabled status

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

## 📚 Resources
---

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Python-Jose JWT](https://python-jose.readthedocs.io/)
- [Passlib Hashing](https://passlib.readthedocs.io/)
- [DBeaver Database Tool](https://dbeaver.io/)

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
