"""Pytest configuration and shared fixtures for testing.

This module provides:
- Test database session
- FastAPI TestClient configuration
- Fixtures for creating test users and expenses
- Mock authentication
"""

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.main import app
from app.database.session import Base, get_db
from app.database.models.user import User
from app.database.models.expense import Expense
from app.core.enums import UserRole, UserStatus, ExpenseCategory
from app.core.security import get_password_hash


# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_db() -> Generator[None, None, None]:
    """Create test database tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """Provide a clean database session for each test."""
    # Create fresh tables
    Base.metadata.create_all(bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db: Session) -> TestClient:
    """Provide a TestClient with overridden dependencies."""
    return TestClient(app)


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user in the database."""
    user = User(
        username="testuser",
        hashed_password=get_password_hash(
            "testpassword123"  # pragma: allowlist secret
        ),
        budget=1000.0,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session) -> User:
    """Create a test admin user in the database."""
    admin = User(
        username="testadmin",
        hashed_password=get_password_hash(
            "adminpassword123"  # pragma: allowlist secret
        ),
        budget=5000.0,
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def test_pending_user(db: Session) -> User:
    """Create a test user with PENDING status (awaiting admin approval)."""
    user = User(
        username="pendinguser",
        hashed_password=get_password_hash("pendingpass123"),
        budget=800.0,
        role=UserRole.USER,
        status=UserStatus.PENDING,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_expense(db: Session, test_user: User) -> Expense:
    """Create a test expense for test_user."""
    from datetime import datetime

    expense = Expense(
        description="Test meal",
        amount=25.50,
        category=ExpenseCategory.FOOD,
        user_id=test_user.id,
        date=datetime.utcnow(),
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@pytest.fixture
def auth_token(client: TestClient, test_user: User) -> str:
    """Obtain JWT token for test_user."""
    response = client.post(
        "/token",
        data={
            "username": "testuser",
            "password": "testpassword123",  # pragma: allowlist secret
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest.fixture
def admin_auth_token(client: TestClient, test_admin: User) -> str:
    """Obtain JWT token for test_admin."""
    response = client.post(
        "/token",
        data={
            "username": "testadmin",
            "password": "adminpassword123",  # pragma: allowlist secret
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token


@pytest.fixture
def authenticated_client(client: TestClient, auth_token: str) -> TestClient:
    """TestClient with authentication header for test_user."""
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client


@pytest.fixture
def admin_client(client: TestClient, admin_auth_token: str) -> TestClient:
    """TestClient with authentication header for test_admin."""
    client.headers.update({"Authorization": f"Bearer {admin_auth_token}"})
    return client


@pytest.fixture
def multiple_expenses(db: Session, test_user: User) -> list[Expense]:
    """Create multiple test expenses for bulk testing."""
    from datetime import datetime, timedelta

    expenses = []
    base_date = datetime.utcnow()
    categories = [
        ExpenseCategory.FOOD,
        ExpenseCategory.TRANSPORTATION,
        ExpenseCategory.ENTERTAINMENT,
    ]

    for i in range(6):
        expense = Expense(
            description=f"Expense {i+1}",
            amount=10.0 + i * 5,
            category=categories[i % len(categories)],
            user_id=test_user.id,
            date=base_date - timedelta(days=i),
        )
        db.add(expense)
        expenses.append(expense)

    db.commit()
    for expense in expenses:
        db.refresh(expense)

    return expenses
