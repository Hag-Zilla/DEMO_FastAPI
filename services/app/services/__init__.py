"""Services module for business logic encapsulation.

This module contains all business logic separated from FastAPI routers,
following FastAPI best practices for larger applications.

Services:
    - auth_service: Authentication, token management, user verification
    - user_service: User CRUD, validation, admin workflows
    - expense_service: Expense CRUD, filtering, aggregation
    - alert_service: Budget alerts and threshold monitoring
    - report_service: Analytics and reporting features
"""

from .auth_service import AuthService
from .user_service import UserService
from .expense_service import ExpenseService
from .alert_service import AlertService
from .report_service import ReportService

__all__ = [
    "AuthService",
    "UserService",
    "ExpenseService",
    "AlertService",
    "ReportService",
]
