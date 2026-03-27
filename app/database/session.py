"""Database session management and Base declarative class."""

# ============================================================================
# IMPORTS
# ============================================================================

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings


# ============================================================================
# CONFIGURATION / CONSTANTS
# ============================================================================

# Database configuration
DATABASE_URL = settings.DATABASE_URL

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

# Base class for models
Base = declarative_base()


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
