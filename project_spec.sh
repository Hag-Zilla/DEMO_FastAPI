#!/bin/bash

set -euo pipefail
umask 077

# This script prompts for an admin password and creates/updates the admin account.
# It does not persist this secret in .env because app settings forbid unknown env keys.

BOOTSTRAP_LOCK_FILE=".admin_bootstrap_done"

if [ -f "${BOOTSTRAP_LOCK_FILE}" ] && [ "${ADMIN_BOOTSTRAP_FORCE:-0}" != "1" ]; then
    echo "Admin bootstrap already completed. Skipping."
    echo "To force a rerun, execute: ADMIN_BOOTSTRAP_FORCE=1 bash project_spec.sh"
    exit 0
fi

ADMIN_EXISTS=$(python <<'EOF'
from app.database.models.expense import Expense  # noqa: F401
from app.database.models.user import User
from app.database.session import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    admin = db.query(User).filter(User.username == "admin").first()
    print("1" if admin else "0")
finally:
    db.close()
EOF
)

if [ "${ADMIN_EXISTS}" = "1" ]; then
    read -r -p "Admin user already exists. Overwrite password and re-enable admin account? (yes/no): " OVERWRITE_CONFIRM
    if [ "${OVERWRITE_CONFIRM}" != "yes" ]; then
        echo "Admin bootstrap cancelled by user."
        exit 0
    fi
fi

read -r -s -p "Enter your ADM_SECRET_KEY for the admin account: " ADM_SECRET_KEY
echo

if [ -z "${ADM_SECRET_KEY}" ]; then
  echo "Error: ADM_SECRET_KEY cannot be empty."
  exit 1
fi

if [ "${#ADM_SECRET_KEY}" -lt 12 ]; then
    echo "Error: admin secret must be at least 12 characters long."
    exit 1
fi
if ! printf '%s' "${ADM_SECRET_KEY}" | grep -q '[A-Z]'; then
    echo "Error: admin secret must contain at least one uppercase letter."
    exit 1
fi
if ! printf '%s' "${ADM_SECRET_KEY}" | grep -q '[a-z]'; then
    echo "Error: admin secret must contain at least one lowercase letter."
    exit 1
fi
if ! printf '%s' "${ADM_SECRET_KEY}" | grep -q '[0-9]'; then
    echo "Error: admin secret must contain at least one digit."
    exit 1
fi
if ! printf '%s' "${ADM_SECRET_KEY}" | grep -q '[^A-Za-z0-9]'; then
    echo "Error: admin secret must contain at least one special character."
    exit 1
fi

# Cleanup legacy key if present from previous script versions
if [ -f .env ] && grep -q '^ADM_SECRET_KEY=' .env; then
  sed -i '/^ADM_SECRET_KEY=/d' .env
  echo "Removed legacy ADM_SECRET_KEY from .env to keep app settings valid."
fi

ADM_SECRET_KEY="${ADM_SECRET_KEY}" python <<'EOF'
import os

from passlib.context import CryptContext

from app.core.enums import UserRole
from app.database.models.expense import Expense  # noqa: F401
from app.database.models.user import User
from app.database.session import Base, SessionLocal, engine

admin_password = os.getenv("ADM_SECRET_KEY")
if not admin_password:
    raise ValueError("ADM_SECRET_KEY is not available for admin bootstrap.")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Ensure all tables are available when bootstrapping standalone
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    admin_user = db.query(User).filter(User.username == "admin").first()
    hashed_password = pwd_context.hash(admin_password)

    if admin_user is None:
        admin_user = User(
            username="admin",
            hashed_password=hashed_password,
            budget=0.0,
            role=UserRole.ADMIN,
            disabled=False,
        )
        db.add(admin_user)
        db.commit()
        print("Admin user created with username: admin")
    else:
        admin_user.hashed_password = hashed_password
        admin_user.role = UserRole.ADMIN
        admin_user.disabled = False
        db.commit()
        print("Admin user updated (password/role/disabled).")
finally:
    db.close()
EOF

echo "Admin bootstrap completed."

date -u +"%Y-%m-%dT%H:%M:%SZ" > "${BOOTSTRAP_LOCK_FILE}"
chmod 600 "${BOOTSTRAP_LOCK_FILE}"
echo "One-shot lock written to ${BOOTSTRAP_LOCK_FILE}."