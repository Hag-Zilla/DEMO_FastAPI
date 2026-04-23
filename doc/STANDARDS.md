# 📋 Code Standards & Best Practices

This document outlines the coding standards and conventions for DEMO_FastAPI.

---

## Table of Contents

1. [File Organization](#file-organization)
2. [Python Code Structure](#python-code-structure)
3. [Naming Conventions](#naming-conventions)
4. [Docstrings](#docstrings)
5. [Type Hints](#type-hints)
6. [Import Organization](#import-organization)
7. [Error Handling](#error-handling)
8. [Testing](#testing)

---

## File Organization

### Directory Structure

```
DEMO_FastAPI/
├── services/
│   └── api/                        # FastAPI package (services.api)
│       ├── main.py                 # FastAPI application instance
│       ├── auth/                   # Auth module (router/schemas/service)
│       ├── core/                   # Config, security, exceptions, middleware
│       ├── database/               # SQLAlchemy session + ORM models
│       ├── routers/                # API routers (users, expenses, reports, ...)
│       ├── schemas/                # Pydantic schemas
│       ├── services/               # Business logic layer
│       ├── utils/                  # Dependencies, branding, static assets
│       └── tests/                  # Pytest test suite + load tests
├── doc/                            # Project documentation
├── startup/                        # project_spec.sh (admin bootstrap)
├── pyproject.toml                  # Workspace root (uv orchestration)
├── services/
│   └── api/
│       └── pyproject.toml          # API service metadata, deps, and tool config
├── uv.lock                         # Locked dependency versions
└── Makefile                        # Common local development commands
```

---

## Python Code Structure

Every Python file follows this consistent structure:

### 1. File Docstring

```python
"""Brief module description in one line.

Optional longer description if needed. Explain what this module does,
its key components, and design decisions.
"""
```

### 2. Imports Section

```python
# ============================================================================
# IMPORTS
# ============================================================================

# Standard library (alphabetical)
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated, Dict, List, Optional

# Third-party packages (alphabetical)
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

# Local imports (absolute, alphabetical)
from services.api.core.config import settings
from services.api.core.security import get_current_user
from services.api.database.models.user import User
from services.api.schemas.user import UserResponse
```

**Rules**:
- Organize: stdlib → third-party → local
- Alphabetical within each group
- Prefer absolute imports for cross-package references (`services.api...`)
- Relative imports are acceptable inside the same package when they improve readability
- Import specific names, not entire modules (except `import json`)
- Group related imports together

### 3. Configuration & Constants

```python
# ============================================================================
# CONFIGURATION / CONSTANTS
# ============================================================================

# Module-level constants (SCREAMING_SNAKE_CASE)
CACHE_TTL_SECONDS = 3600
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30.0

# Private constants (prefixed with _)
_URL_PATTERN = re.compile(r"^https?://")
_INTERNAL_BUFFER_SIZE = 1024

# Configuration from settings
DEBUG = settings.DEBUG
MAX_BATCH_SIZE = getattr(settings, "MAX_BATCH_SIZE", 100)
```

**Rules**:
- Public: `CONSTANT_NAME` (SCREAMING_SNAKE_CASE)
- Private: `_constant_name` (with underscore prefix)
- Configuration loaded from `settings`
- No magic numbers in code

### 4. Private Helpers

```python
# ============================================================================
# PRIVATE HELPERS
# ============================================================================

def _format_timestamp(dt: datetime) -> str:
    """Internal helper to format datetime.

    Args:
        dt: Datetime to format.

    Returns:
        ISO format string.
    """
    return dt.isoformat()

def _validate_email(email: str) -> bool:
    """Check if email is valid format.

    Args:
        email: Email string to validate.

    Returns:
        True if valid, False otherwise.
    """
    return "@" in email and "." in email.split("@")[-1]

async def _fetch_user_from_db(user_id: int, db: Session) -> Optional[User]:
    """Internal async helper to fetch user.

    Args:
        user_id: User ID to fetch.
        db: Database session.

    Returns:
        User object or None if not found.
    """
    return db.query(User).filter(User.id == user_id).first()
```

**Rules**:
- Private functions start with `_` underscore
- Internal-only functions go here
- Required to have docstrings
- Use type hints on all parameters and returns
- Async functions when needed

### 5. Public Classes & Functions

```python
# ============================================================================
# PUBLIC CLASSES / FUNCTIONS
# ============================================================================

class UserService:
    """Service for user operations.

    Handles user creation, retrieval, updates, and deletions.
    Encapsulates business logic separate from HTTP handlers.
    """

    def __init__(self, db: Session):
        """Initialize service with database session.

        Args:
            db: Configured database session.
        """
        self.db = db

    def get_user(self, user_id: int) -> User:
        """Retrieve user by ID.

        Args:
            user_id: User ID to retrieve.

        Returns:
            User object.

        Raises:
            ValueError: If user not found.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        return user

async def create_expense(
    data: ExpenseCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> ExpenseResponse:
    """Create new expense for current user.

    Args:
        data: Expense creation data.
        current_user: Authenticated user from dependency.
        db: Database session from dependency.

    Returns:
        Created expense response.

    Raises:
        ValueError: If data validation fails.
    """
    # Implementation
    pass
```

**Rules**:
- Public classes/functions have NO underscore prefix
- All public items MUST have docstrings
- Type hints on all parameters and returns
- Async for I/O operations (database, HTTP clients)
- Raise specific exceptions with messages

### 6. Module Setup & Exports

```python
# ============================================================================
# MODULE SETUP / EXPORTS
# ============================================================================

# Explicitly define public API
__all__ = [
    "UserService",
    "create_expense",
    "ExpenseCreate",
]

# Initialize routers
router = APIRouter(prefix="/expenses", tags=["expenses"])

# Register routes
@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> List[ExpenseResponse]:
    """List all expenses for current user."""
    pass
```

**Rules**:
- Define `__all__` for explicit API surface
- Initialize class instances (routers, databases)
- Register final routes/listeners

### 7. CLI / Main (if applicable)

```python
# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    """Execute when script is run directly."""
    import uvicorn

    uvicorn.run(
        "services.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
```

---

## Naming Conventions

### Variables & Functions

```python
# ✅ GOOD
user_count = 42
is_active = True
process_payment()
validate_email()
get_user_by_id()

# ❌ BAD
uc = 42                    # Too short
isActive = True             # camelCase (use snake_case)
ProcessPayment()            # PascalCase for functions
validate_Email()            # Inconsistent naming
GetUserByID()              # Wrong case
```

### Classes & Types

```python
# ✅ GOOD
class UserService:
    pass

class EmailValidator:
    pass

class HTTPClient:
    pass

# ❌ BAD
class userService:         # Should be PascalCase
class email_validator:     # Should be PascalCase
class HTTPclient:          # Inconsistent
```

### Constants

```python
# ✅ GOOD
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30
DATABASE_URL = "postgresql://..."

# ❌ BAD
max_retries = 3            # Should be SCREAMING_SNAKE_CASE
maxRetries = 3             # camelCase, not constant-like
Max_Retries = 3            # Mixed case
```

### Private Items

```python
# ✅ GOOD
def _internal_helper():
    pass

_config_cache = {}
_logger = logging.getLogger(__name__)

# ❌ BAD
def internal_helper():     # Should have _ prefix for internal
config_cache = {}          # Should have _ prefix
__private_var = 0          # Double underscore only for name mangling
```

---

## Docstrings

Use **Google-style docstrings** ([PEP 257](https://www.python.org/dev/peps/pep-0257/) compatible).

### Function Docstrings

```python
def calculate_total_expense(
    expenses: List[Expense],
    user_id: int,
    include_archived: bool = False,
) -> float:
    """Calculate total expenses for a user.

    Sums all expenses for the specified user. Can optionally include
    archived expenses in the total.

    Args:
        expenses: List of expense objects to sum.
        user_id: ID of user to filter by.
        include_archived: Whether to include archived expenses. Defaults to False.

    Returns:
        Total amount as float. Returns 0.0 if no expenses found.

    Raises:
        ValueError: If user_id is negative.
        TypeError: If expenses is not a list.

    Example:
        >>> expenses = [Expense(amount=10), Expense(amount=20)]
        >>> total = calculate_total_expense(expenses, user_id=1)
        >>> print(total)
        30.0
    """
    pass
```

### Class Docstrings

```python
class ExpenseManager:
    """Manager for expense operations.

    Handles creation, retrieval, updating, and deletion of expenses.
    Includes validation and authorization checks.

    Attributes:
        db: Database session instance.
        logger: Logger for this manager.

    Example:
        >>> manager = ExpenseManager(db_session)
        >>> expense = manager.create_expense(data, user_id=1)
        >>> print(expense.id)
        123
    """

    def __init__(self, db: Session):
        """Initialize manager with database session.

        Args:
            db: SQLAlchemy Session instance.
        """
        self.db = db

    def create(self, data: ExpenseCreate, user_id: int) -> Expense:
        """Create new expense.

        Args:
            data: Expense creation schema.
            user_id: Owner user ID.

        Returns:
            Created expense object.

        Raises:
            ValueError: If data is invalid.
        """
        pass
```

### Module Docstrings

```python
"""User authentication and authorization.

Provides login, token generation, JWT validation, and permission checks.

This module handles:
- User login and token exchange
- JWT token creation and validation
- Role-based access control (RBAC)
- Dependency injection for FastAPI

Example:
    >>> from services.api.core.security import get_current_user
    >>> from fastapi import Depends
    >>>
    >>> @app.get("/profile")
    >>> async def get_profile(user = Depends(get_current_user)):
    >>>     return {"user": user.username}
"""
```

---

## Type Hints

Use type hints on ALL public functions and class methods.

### Basic Types

```python
from typing import Dict, List, Optional, Set, Tuple, Union

def process_items(items: List[str]) -> Set[str]:
    """Convert list to set."""
    return set(items)

def get_config(key: str) -> Optional[str]:
    """Get config value, returns None if not found."""
    pass

def merge_dicts(d1: Dict[str, int], d2: Dict[str, int]) -> Dict[str, int]:
    """Merge two dictionaries."""
    pass

def parse_version(version_str: str) -> Tuple[int, int, int]:
    """Parse version string to tuple."""
    return tuple(int(x) for x in version_str.split("."))
```

### Union & Optional

```python
from typing import Union

# Union: accepts one of multiple types
def process(value: Union[str, int]) -> str:
    """Convert value to string."""
    return str(value)

# Optional: equivalent to Union[T, None]
def get_user(user_id: int) -> Optional[User]:
    """Get user or None."""
    pass

# Better: use | syntax (Python 3.10+)
def process_v2(value: str | int) -> str:
    """Alternative syntax."""
    return str(value)
```

### Annotated for Dependencies

```python
from typing import Annotated
from fastapi import Depends

# Use Annotated for FastAPI dependencies
async def get_current_user(token: str) -> User:
    """Verify token and return user."""
    pass

@app.get("/profile")
async def profile(
    user: Annotated[User, Depends(get_current_user)]
) -> UserResponse:
    """Get profile of authenticated user."""
    pass
```

### Generic Types

```python
from typing import Generic, TypeVar

T = TypeVar("T")  # Generic type variable

class Repository(Generic[T]):
    """Generic repository for any entity type."""

    def get(self, item_id: int) -> Optional[T]:
        """Get item by ID."""
        pass

    def list(self) -> List[T]:
        """List all items."""
        pass

# Usage
user_repo: Repository[User] = UserRepository(db)
expense_repo: Repository[Expense] = ExpenseRepository(db)
```

---

## Import Organization

### Rule Order

1. **Standard library** (built-in modules)
2. **Third-party** (external packages)
3. **Local** (project modules)

Alphabetical within each group.

### Good Example

```python
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Annotated, Dict, List, Optional

import yaml
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.exceptions import NotFoundError
from ..core.security import get_current_user
from ..database.models import User
from ..schemas import UserCreate, UserResponse
from ..utils.dependencies import get_db
```

### Tools for Formatting

Pre-commit hooks automatically fix common issues:

```bash
# Run import sorting
ruff check --fix services/api

# Or let pre-commit handle it
make run-hooks
```

---

## Error Handling

### Define Custom Exceptions

```python
# In services/api/core/exceptions.py

class APIError(Exception):
    """Base exception for API errors."""
    pass

class NotFoundError(APIError):
    """Resource not found."""
    pass

class AuthorizationError(APIError):
    """User not authorized."""
    pass

class ValidationError(APIError):
    """Invalid input data."""
    pass
```

### Raise with Context

```python
# ✅ GOOD
if not user:
    raise NotFoundError(f"User {user_id} not found")

try:
    process_payment()
except StripeError as e:
    raise PaymentError(f"Payment failed: {e}") from e

# ❌ BAD
if not user:
    raise Exception("error")  # Too generic

try:
    process_payment()
except Exception:
    pass  # Silent failures are bad

raise Exception("User not found")  # Bare Exception class
```

### FastAPI Error Responses

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int) -> UserResponse:
    """Get user by ID.

    Raises:
        HTTPException: 404 if user not found.
    """
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User {user_id} not found"
        )
    return user
```

---

## Testing

### Test File Structure

```
services/api/tests/
├── __init__.py
├── conftest.py             # Shared fixtures
├── test_auth.py            # Authentication tests
├── test_users.py           # User management tests
├── test_expenses.py        # Expense tests
├── test_alerts.py          # Alert tests
├── test_reports.py         # Report tests
├── test_security.py        # Security tests
├── test_contract.py        # OpenAPI contract tests
└── load_tests/
    └── locustfile.py       # Locust scenarios
```

### Naming Convention

```python
def test_create_user_success():
    """Test successful user creation."""
    pass

def test_create_user_duplicate_username():
    """Test user creation fails with duplicate username."""
    pass

def test_get_user_not_found():
    """Test retrieving non-existent user raises error."""
    pass

class TestUserService:
    """Tests for UserService class."""

    def test_get_existing_user(self):
        """Test retrieving existing user."""
        pass

    def test_update_user_permissions(self):
        """Test updating user permissions."""
        pass
```

### Fixtures

```python
# In conftest.py

import pytest
from sqlalchemy.orm import Session

from services.api.core.config import settings
from services.api.database.session import SessionLocal, Base, engine


@pytest.fixture
def db():
    """Provide test database session."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db: Session):
    """Create test user."""
    from services.api.database.models import User
    user = User(username="testuser", hashed_password="...")
    db.add(user)
    db.commit()
    return user
```

---

## Quick Checklist

Before committing Python code:

- [ ] File has docstring
- [ ] Sections properly separated with `# ===` dividers
- [ ] Imports: stdlib → third-party → local, alphabetical
- [ ] Public items: NO underscore, have docstrings
- [ ] Private items: `_prefix`, have docstrings
- [ ] All public functions have type hints
- [ ] Docstrings use Google style
- [ ] Constants are SCREAMING_SNAKE_CASE
- [ ] Classes are PascalCase
- [ ] Functions/variables are snake_case
- [ ] No magic numbers (use constants)
- [ ] Error messages are descriptive
- [ ] Tests written and passing
- [ ] Pre-commit hooks pass (`make run-hooks`)

---

## References

- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [PEP 8 - Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Last Updated**: 2026-04-22
**Version**: 1.1
