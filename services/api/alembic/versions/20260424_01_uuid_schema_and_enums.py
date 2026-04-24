"""Create users and expenses tables with UUID string keys.

Revision ID: 20260424_01
Revises:
Create Date: 2026-04-24
"""

from alembic import op
import sqlalchemy as sa


revision = "20260424_01"
down_revision = None
branch_labels = None
depends_on = None


user_role_enum = sa.Enum("ADMIN", "USER", "MODERATOR", name="userrole")
user_status_enum = sa.Enum("PENDING", "ACTIVE", "DISABLED", name="userstatus")
expense_category_enum = sa.Enum(
    "FOOD",
    "TRANSPORTATION",
    "ENTERTAINMENT",
    "UTILITIES",
    "HEALTHCARE",
    "EDUCATION",
    "SHOPPING",
    "OTHER",
    name="expensecategory",
)


def upgrade() -> None:
    """Create users/expenses schema with UUID string identifiers if missing."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "users" not in existing_tables:
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("username", sa.String(), nullable=True),
            sa.Column("hashed_password", sa.String(), nullable=True),
            sa.Column("budget", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("role", user_role_enum, nullable=True),
            sa.Column("status", user_status_enum, nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
        op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    if "expenses" not in existing_tables:
        op.create_table(
            "expenses",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("category", expense_category_enum, nullable=True),
            sa.Column("user_id", sa.String(length=36), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_expenses_id"), "expenses", ["id"], unique=False)


def downgrade() -> None:
    """Drop users/expenses schema objects created by this revision."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "expenses" in existing_tables:
        op.drop_index(op.f("ix_expenses_id"), table_name="expenses")
        op.drop_table("expenses")

    if "users" in existing_tables:
        op.drop_index(op.f("ix_users_username"), table_name="users")
        op.drop_index(op.f("ix_users_id"), table_name="users")
        op.drop_table("users")
