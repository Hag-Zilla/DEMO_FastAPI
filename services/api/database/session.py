"""Database session management and Base declarative class."""

# ============================================================================
# IMPORTS
# ============================================================================

from pathlib import Path
from typing import cast

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.api.core.config import settings
from services.api.database.base import Base


# ============================================================================
# CONFIGURATION / CONSTANTS
# ============================================================================

__all__ = ["Base", "engine", "SessionLocal", "get_db", "run_migrations"]

# Database configuration
DATABASE_URL = cast(str, settings.DATABASE_URL)  # pylint: disable=no-member

engine_kwargs: dict = {}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    engine_kwargs["poolclass"] = StaticPool

    if DATABASE_URL.startswith("sqlite:///"):
        DB_PATH = DATABASE_URL.replace("sqlite:///", "", 1)
        if DB_PATH and DB_PATH != ":memory:" and not DB_PATH.startswith("file:"):
            Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


# ============================================================================
# MODULE SETUP
# ============================================================================

# Create the database engine
engine = create_engine(DATABASE_URL, **engine_kwargs)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ============================================================================
# PUBLIC FUNCTIONS
# ============================================================================


def get_db():
    """Dependency to retrieve a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Apply Alembic migrations up to head.

    This keeps schema evolution explicit and reproducible across environments
    instead of relying on ``Base.metadata.create_all`` at runtime.
    """
    service_dir = Path(__file__).resolve().parent.parent
    alembic_ini = service_dir / "alembic.ini"
    alembic_dir = service_dir / "alembic"

    if not alembic_ini.exists() or not alembic_dir.exists():
        return

    alembic_cfg = Config(str(alembic_ini))
    alembic_cfg.set_main_option("script_location", str(alembic_dir))
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.upgrade(alembic_cfg, "head")
