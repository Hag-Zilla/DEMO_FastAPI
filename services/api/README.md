# API Service Documentation

Detailed technical documentation for the FastAPI service in `services/api`.

## Table of Contents

- [Data Structures](#data-structures)
  - [Enums](#enums)
  - [ORM Models and Database Schema](#orm-models-and-database-schema)
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
  - [Analytics](#analytics)
  - [Health](#health)
- [Authentication and Authorization](#authentication-and-authorization)
  - [User Status Workflow](#user-status-workflow)
  - [Role Hierarchy](#role-hierarchy)
  - [Access Control Details](#access-control-details)
- [Exception Handling](#exception-handling)

## Data Structures

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

### ORM Models and Database Schema

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
| user_id | STRING(36) | Foreign Key -> users.id | Expense owner |

**ORM Model**: `services/api/database/models/expense.py`

### API Request/Response Models

Defined in `services/api/schemas/`, these Pydantic models validate and serialize API requests/responses:

**User Operations**
- `UserCreate`: username, password (min 6 chars), budget (>= 0, defaults to 0.0)
- `UserSelfUpdate`: username/password/budget only (extra fields forbidden)
- `UserUpdate`: admin update schema (username, password, budget, role, status)
- `UserResponse`: includes id, role, status

**Expense Operations**
- `ExpenseCreate`: description, amount (> 0), category enum
- `ExpenseUpdate`: all fields optional
- `ExpenseResponse`: includes id, datetime, user_id

### Managing the Database

Use [DBeaver Community Edition](https://dbeaver.io/) to browse and edit your SQLite database graphically.

Important: Stop the API server before making manual database changes to avoid file locks.

### Database Migration

The application uses **Alembic** for schema management.

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

## API Endpoints

### Role-Based Access Control

All endpoints have defined permission requirements:

- **PUBLIC**: No authentication required
- **USER**: Any authenticated user with `status=ACTIVE`
- **MODERATOR**: MODERATOR or ADMIN role
- **ADMIN**: ADMIN role only

### Authentication

- `POST /token` - Login with username/password, returns JWT token

### User Management

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/users/create` | POST | PUBLIC | Create new user account (starts with status: PENDING) |
| `/users/create-active` | POST | PUBLIC | Create user with ACTIVE status (dev/test only) |
| `/users/me` | GET | USER | Get authenticated user's profile |
| `/users/` | GET | ADMIN | List all users (filterable by status: pending/active/disabled) |
| `/users/update/` | PUT | USER | Update own profile (username, password, budget only) |
| `/users/update/{user_id}/` | PUT | ADMIN | Update any user (role, status, all fields) |
| `/users/{user_id}/approve` | POST | MODERATOR+ADMIN | Approve PENDING user -> ACTIVE |
| `/users/{user_id}/reject` | POST | MODERATOR+ADMIN | Reject PENDING user -> DISABLED |
| `/users/{user_id}/disable` | POST | MODERATOR+ADMIN | Suspend ACTIVE user -> DISABLED |
| `/users/{user_id}/reactivate` | POST | MODERATOR+ADMIN | Reactivate DISABLED user -> ACTIVE |
| `/users/delete/{user_id}/` | DELETE | ADMIN | Delete user (admins cannot delete themselves) |

### Expenses

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/expenses/` | GET | USER | List authenticated user's expenses |
| `/expenses/` | POST | USER | Add new expense |
| `/expenses/{expense_id}` | GET | USER | Get one expense by ID (must own it) |
| `/expenses/{expense_id}` | PUT | USER | Update expense (must own it) |
| `/expenses/{expense_id}` | DELETE | USER | Delete expense (must own it) |

### Reports

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/reports/monthly/{year}/{month}` | GET | USER | Monthly expense summary (authenticated user) |
| `/reports/period` | GET | USER | Custom period report (authenticated user) |
| `/reports/all` | GET | ADMIN | All users' reports (admin only) |

### Alerts

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/alerts/` | GET | USER | Check for budget overruns |

### Analytics

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/analytics/` | GET | ADMIN | Business KPIs snapshot (user counts, expense totals, in-memory counters) |

### Health

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/health/live` | GET | PUBLIC | Process liveness check |
| `/health/ready` | GET | PUBLIC | Readiness check (includes database ping) |
| `/health/startup` | GET | PUBLIC | Startup phase completion check |
| `/health` | GET | PUBLIC | Legacy alias for liveness |

## Authentication and Authorization

### User Status Workflow

New users follow an approval workflow before they can access the API:

```text
1. User Registration (POST /users/create)
   ↓
   Status: PENDING (cannot login)
   ↓
2. Admin/Moderator Reviews
   ↓
  ├─→ POST /users/{id}/approve → Status: ACTIVE (can login)
   └─→ POST /users/{id}/reject  → Status: DISABLED
   ↓
3. Active User Lifecycle
   ↓
  ├─→ POST /users/{id}/disable    → Status: DISABLED
   └─→ POST /users/{id}/reactivate → Status: ACTIVE
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

## Exception Handling

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
