"""Shared SQLAlchemy declarative base.

Separated from session/bootstrap code so tools like Alembic can import model
metadata without triggering full application settings loading.
"""

from sqlalchemy.orm import declarative_base


Base = declarative_base()
