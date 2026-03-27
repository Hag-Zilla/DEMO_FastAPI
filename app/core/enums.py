"""Enums for the application."""

from enum import Enum


class ExpenseCategory(str, Enum):
    """Expense categories."""

    FOOD = "food"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    SHOPPING = "shopping"
    OTHER = "other"


class UserRole(str, Enum):
    """User roles."""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class UserStatus(str, Enum):
    """User account status."""

    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"
