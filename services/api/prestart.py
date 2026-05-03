"""Pre-start checks for database connectivity before app startup."""

from __future__ import annotations

import time

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from services.api.core.logging import get_logger
from services.api.database.session import engine

logger = get_logger(__name__)

MAX_TRIES = 60
WAIT_SECONDS = 1


def wait_for_database() -> None:
    """Retry DB connection until it becomes available or timeout is reached."""
    for attempt in range(1, MAX_TRIES + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connectivity check succeeded")
            return
        except (SQLAlchemyError, TimeoutError, OSError) as exc:  # pragma: no cover
            logger.warning(
                "Database not ready yet (attempt %s/%s): %s",
                attempt,
                MAX_TRIES,
                exc,
            )
            if attempt == MAX_TRIES:
                raise
            time.sleep(WAIT_SECONDS)


def main() -> None:
    """Run all pre-start checks."""
    logger.info("Running pre-start checks")
    wait_for_database()


if __name__ == "__main__":
    main()
