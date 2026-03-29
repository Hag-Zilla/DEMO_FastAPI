# Testing Guide

This directory contains automated tests for the DEMO_FastAPI application using **pytest** and **FastAPI's TestClient**.

## Overview

| Component | Status | Coverage |
|-----------|--------|----------|
| **test_auth.py** | ✅ Login/Token | `/token`, `/users/me` |
| **test_users.py** | ✅ User Management | User CRUD, admin operations |
| **test_expenses.py** | ✅ Expense CRUD | Create, read, update, delete, filtering |
| **test_alerts.py** | 🔜 (placeholder) | Budget alerts endpoint |
| **test_reports.py** | 🔜 (placeholder) | Report generation endpoints |

---

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
pytest tests/test_users.py
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestLogin
pytest tests/test_users.py::TestAdminUserOperations
```

### Run Specific Test Function
```bash
pytest tests/test_auth.py::TestLogin::test_login_success
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html to view detailed report
```

### Run with Verbose Output
```bash
pytest -v
pytest -vv  # Extra verbose
```

### Run with Markers (Advanced)
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Run only integration tests
```

---

## Test Structure

### Fixtures (conftest.py)

**Database & Client**
- `db` - Clean in-memory SQLite session for each test
- `client` - FastAPI TestClient with dependency overrides

**Test Users**
- `test_user` - Standard ACTIVE user
- `test_admin` - Admin ACTIVE user
- `test_pending_user` - User waiting for approval

**Authentication**
- `auth_token` - JWT token for test_user
- `admin_auth_token` - JWT token for test_admin
- `authenticated_client` - TestClient with Bearer token header
- `admin_client` - TestClient with admin Bearer token header

**Test Data**
- `test_expense` - Sample expense for test_user
- `multiple_expenses` - 6 expenses with different categories

### Example Test
```python
def test_login_success(self, client: TestClient, test_user: User) -> None:
    """Test successful login returns JWT token."""
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
```

---

## Test Categories

### Authentication Tests (test_auth.py)
- User login with valid/invalid credentials
- Token format validation
- Current user retrieval
- Authentication header validation

### User Management Tests (test_users.py)
- User account creation
- Username uniqueness validation
- Admin approval workflow
- Admin user listing and filtering
- Self-service profile updates
- Permission checks

### Expense Tests (test_expenses.py)
- Create, read, update, delete operations
- Category filtering
- Date range filtering
- User data isolation (users see only own expenses)
- Admin access (see all expenses)
- Authorization checks

---

## Database in Tests

Tests use **in-memory SQLite** for speed and isolation.

### Key Points
- Each test gets a clean database
- Transactions roll back after each test
- No side effects between tests
- Models from `app/database/models/` are auto-created

### Accessing Database in Tests
```python
def test_something(self, db: Session) -> None:
    """Access database directly if needed."""
    user = db.query(User).filter(User.username == "testuser").first()
    assert user is not None
```

---

## Authentication in Tests

### Login and Get Token
```python
def test_with_token(self, client: TestClient) -> None:
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    
    # Use token in subsequent requests
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
```

### Using Authenticated Client Fixture
```python
def test_with_fixture(self, authenticated_client: TestClient) -> None:
    """Headers already set by fixture."""
    response = authenticated_client.get("/users/me")
    assert response.status_code == 200
```

---

## Writing New Tests

### 1. Create Test Class
```python
class TestMyFeature:
    """Test cases for my feature."""
```

### 2. Use Fixtures
```python
def test_something(self, db: Session, authenticated_client: TestClient) -> None:
    """Test with database and authenticated client."""
```

### 3. Make Request
```python
response = authenticated_client.post(
    "/endpoint",
    json={"field": "value"},
)
```

### 4. Assert Response
```python
assert response.status_code == 201
assert response.json()["field"] == "value"
```

### 5. Verify Database State (if needed)
```python
user = db.query(User).filter(User.id == user_id).first()
assert user is not None
```

---

## Common Assertions

```python
# Status codes
assert response.status_code == 200
assert response.status_code in [200, 201]

# JSON response
data = response.json()
assert data["username"] == "testuser"

# Error responses
assert "error" in response.json()
assert "detail" in response.json()

# Database state
user = db.query(User).filter(User.id == 1).first()
assert user is not None
assert user.email == "test@example.com"
```

---

## Debugging Tests

### Print Debug Info
```python
def test_something(self, authenticated_client: TestClient) -> None:
    response = authenticated_client.get("/users/me")
    print(response.json())  # Shows output with pytest -s
    assert response.status_code == 200
```

### Run with Print Output
```bash
pytest -s  # Show print statements
pytest -vv # Very verbose
```

### Run Single Test
```bash
pytest tests/test_auth.py::TestLogin::test_login_success -vv
```

### Use pdb Debugger
```python
def test_something(self, client: TestClient) -> None:
    response = client.get("/")
    breakpoint()  # Code stops here; inspect variables
```

---

## CI/CD Integration

Tests run automatically in GitHub Actions workflows:
- **`.github/workflows/ci-light.yml`** - Runs on push to `dev`
- **`.github/workflows/ci-full.yml`** - Runs on push to `main`

See [DEPLOYMENT.md](../doc/DEPLOYMENT.md) for CI/CD details.

---

## Performance Tips

### Speed Up Tests
- Fixtures use in-memory SQLite (fast)
- Use `scope="function"` for isolation
- Avoid real file I/O

### Reduce Data
- Create minimal test data
- Use `test_expense` not `multiple_expenses` if only one needed
- Clean up after tests

---

## Best Practices

✅ **Do:**
- One assertion per test (or related assertions)
- Use descriptive test name: `test_login_with_invalid_password`
- Use fixtures for test data setup
- Test both success and error cases
- Verify database state when needed

❌ **Don't:**
- Depend on test order
- Create shared state between tests
- Test internal implementation details
- Use real databases in tests

---

## Next Steps

1. **Run existing tests**: `pytest tests/`
2. **Check coverage**: `pytest --cov=app`
3. **Add more tests** for uncovered features
4. **Read [Pytest docs](https://docs.pytest.org/)** for advanced features
5. **Auto-run tests** on push with GitHub Actions

---

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'app'
```
- Ensure you run pytest from project root: `cd /path/to/DEMO_FastAPI && pytest`
- Check `PYTHONPATH`: `export PYTHONPATH=$PWD`

### Database Lock Errors
- Tests use in-memory SQLite (no file locks)
- If issues persist, restart Python interpreter

### Fixture Errors
- Ensure fixture names match parameter names exactly
- Fixtures are case-sensitive
- Check `conftest.py` for fixture definitions

---

## Related Documentation

- [DEVELOPMENT.md](../doc/DEVELOPMENT.md) - Development workflow
- [STANDARDS.md](../doc/STANDARDS.md) - Code standards
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
