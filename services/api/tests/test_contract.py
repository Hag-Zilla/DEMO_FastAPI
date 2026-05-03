"""Contract tests using Schemathesis.

Schemathesis auto-generates test cases from the OpenAPI schema and verifies that
every endpoint responds with a documented status code and a well-formed body.

Run via pytest (included in normal test suite)::

    pytest services/api/tests/test_contract.py -v

Or with the Schemathesis CLI for more extensive fuzzing against a live server::

    schemathesis run http://localhost:8000/openapi.json --checks all

See: https://schemathesis.io/
"""

import importlib

import schemathesis
from hypothesis import HealthCheck, settings as hyp_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.api.main import app
from services.api.database.session import get_db
from services.api.database.base import Base


# ---------------------------------------------------------------------------
# Schema fixture — loads OpenAPI spec directly from the ASGI app (no server)
# ---------------------------------------------------------------------------

# Load model modules before create_all so tables are registered in metadata.
importlib.import_module("services.api.database.models.user")
importlib.import_module("services.api.database.models.expense")

schema = schemathesis.openapi.from_asgi("/openapi.json", app)


# ---------------------------------------------------------------------------
# Contract-test database isolation
# ---------------------------------------------------------------------------

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
Base.metadata.create_all(bind=TEST_ENGINE)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# ---------------------------------------------------------------------------
# All endpoints — basic liveness (no 5xx errors, even without credentials)
# ---------------------------------------------------------------------------


@schema.parametrize()
@hyp_settings(
    max_examples=3,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
    deadline=None,
)
def test_no_server_errors(case: schemathesis.Case) -> None:
    """No endpoint returns a 5xx server error, even with invalid/missing auth.

    Protected endpoints are expected to return 401/403/422 for unauthenticated
    requests.  This test only ensures the server does not crash.
    """
    response = case.call()
    assert response.status_code < 500, (
        f"{case.method} {case.formatted_path} returned {response.status_code}: "
        f"{response.text[:200]}"
    )
