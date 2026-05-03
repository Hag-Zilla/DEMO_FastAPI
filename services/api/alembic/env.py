"""Alembic environment configuration for runtime migrations.

This module is executed by Alembic and uses its dynamic ``context`` API.
"""

from __future__ import annotations

import os
from logging.config import fileConfig
from pathlib import Path
import sys
from typing import Any

from alembic import context
from sqlalchemy import engine_from_config, pool

# Pylint cannot statically resolve Alembic's dynamic context proxy members
# (config/configure/begin_transaction/run_migrations/is_offline_mode), and this
# file intentionally performs path bootstrapping before local imports.
# pylint: disable=no-member,wrong-import-position,import-error

alembic_context: Any = context

SERVICE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = SERVICE_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.api.database.base import Base  # noqa: E402
from services.api.database.models import expense as _expense, user as _user  # noqa: E402,F401

# Keep explicit references so static analyzers don't mark these side-effect
# imports as unused; importing models registers tables on Base.metadata.
_MODEL_IMPORTS = (_expense, _user)

config = alembic_context.config


def _read_database_url() -> str:
    """Resolve DATABASE_URL for Alembic without importing full app settings."""
    env_database_url = os.getenv("DATABASE_URL")
    if env_database_url:
        return env_database_url

    repo_root = REPO_ROOT
    for candidate in (repo_root / ".env", repo_root / ".env.example"):
        if not candidate.exists():
            continue
        for line in candidate.read_text(encoding="utf-8").splitlines():
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip()

    raise RuntimeError(
        "DATABASE_URL is required for Alembic. Set it in the environment or root .env."
    )


config.set_main_option("sqlalchemy.url", _read_database_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in offline mode.

    Uses only the configured DB URL and emits SQL without creating a live
    DB connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    alembic_context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        dialect_opts={"paramstyle": "named"},
    )

    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in online mode using a live DB connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        alembic_context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with alembic_context.begin_transaction():
            alembic_context.run_migrations()


if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
