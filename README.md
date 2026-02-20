<div align="center">

# Personal Expense Tracking API

A lightweight FastAPI demo showcasing a complete REST API for expense management with authentication, budgeting, and reporting.

</div>

---

## About

This is a personal expense tracking API built with **FastAPI** and **SQLite**. Users can manage their expenses, set monthly budgets, receive alerts for budget overruns, and generate detailed expense reports. The project demonstrates best practices in API design, authentication, and database modeling.

---

## Features

- **User Management**: Create accounts, authentication via OAuth2, role-based access (admin/user)
- **Expense Tracking**: Add, update, delete expenses with categorization and date tracking
- **Budget Management**: Set global monthly budgets with automatic tracking
- **Alerts**: Get notified when expenses exceed budgeted amounts
- **Reports**: Generate monthly and custom-period expense reports by category
- **Admin Dashboard**: View all users and access system-wide reports

---

## Quick Start

### Prerequisites

- Python 3.11+
- Conda or venv

### Setup Environment

```bash
bash setup.sh
```

The script will guide you through environment setup (Conda or venv) and install all dependencies.

### Run the API

```bash
# Activate environment
conda activate demo_fastapi  # or: source ./venv/bin/activate

# Start the server
uvicorn main:app --reload
```

**API is running at**: http://localhost:8000

---

## Access the API

- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## Project Structure

```
DEMO_FastAPI/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── environment.yml         # Conda environment config
├── setup.sh               # Setup script
│
├── src/
│   ├── config.py          # Configuration
│   ├── schemas.py         # Pydantic models (request/response)
│   ├── auth_manager.py    # Authentication & hashing
│   │
│   ├── database/
│   │   ├── database.py    # SQLAlchemy setup
│   │   └── models.py      # ORM models (User, Expense)
│   │
│   └── routes/
│       ├── user.py        # User endpoints
│       ├── expense.py     # Expense endpoints
│       ├── alert.py       # Alert endpoints
│       ├── report.py      # Report endpoints
│       ├── token.py       # Authentication endpoints
│       └── health.py      # Health check endpoints
```

---

## Database

### Technology

- **Engine**: SQLite (file-based, no server setup required)
- **ORM**: SQLAlchemy
- **Auto-migration**: Tables created automatically on app startup

### Schema

**Users Table**
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key |
| username | STRING | Unique identifier |
| hashed_password | STRING | Bcrypt hashed |
| budget | FLOAT | Monthly budget |
| role | STRING | "user" or "admin" |
| disabled | BOOLEAN | Account status |

**Expenses Table**
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key |
| description | STRING | Expense description |
| amount | FLOAT | Amount spent |
| date | STRING | Date incurred |
| category | STRING | Expense category |
| user_id | INTEGER | Foreign key → users.id |

### Managing the Database

Use [DBeaver Community Edition](https://dbeaver.io/) to browse and edit your SQLite database graphically.

⚠️ **Important**: Stop the API server before making manual database changes to avoid locks.

---

## API Endpoints

### Authentication
- `POST /token` – Login and get JWT token

### User Management
- `POST /users/create` – Create new user
- `GET /users/me` – Get current user profile
- `PUT /users/update/` – Update own profile
- `PUT /users/update/{user_id}/` – Admin: update any user
- `DELETE /users/delete/{user_id}/` – Admin: delete user

### Expenses
- `GET /expenses/` – List user's expenses
- `POST /expenses/` – Add new expense
- `PUT /expenses/{expense_id}` – Update expense
- `DELETE /expenses/{expense_id}` – Delete expense

### Reports
- `GET /reports/monthly/{year}/{month}` – Monthly report
- `GET /reports/period` – Custom period report
- `GET /reports/all` – Admin: all users' reports

### Alerts
- `GET /alerts/` – Check for budget overruns

### Health
- `GET /health` – API status check

---

## Deployment Notes

### For Production

SQLite works fine for small deployments, but consider migrating to PostgreSQL or MySQL for:
- Concurrent write operations
- Multi-instance deployments
- Larger datasets

The modular design allows easy database swaps with minimal code changes.

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/http-basic-auth/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [DBeaver Database Tool](https://dbeaver.io/)
- [FastAPI on Conda](https://anaconda.org/conda-forge/fastapi)

---

## License

See [LICENSE](LICENSE) file for details.
