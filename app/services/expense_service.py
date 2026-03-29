"""Expense management service encapsulating CRUD and filtering logic."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.enums import ExpenseCategory, UserRole
from app.core.exceptions import ResourceNotFoundException, AuthorizationException
from app.core.logging import get_logger
from app.database.models.expense import Expense
from app.database.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

logger = get_logger(__name__)


class ExpenseService:
    """Service handling expense CRUD operations, filtering, and access control."""

    @staticmethod
    def list_expenses_for_user(
        db: Session,
        user_id: int,
        user_role: UserRole,
        category: Optional[ExpenseCategory] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Expense]:
        """
        List expenses with optional filtering.

        Admins can see all expenses, regular users only their own.

        Args:
            db: Database session
            user_id: Current user ID
            user_role: Current user role
            category: Optional expense category filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of Expense objects
        """
        # Admins see all expenses; regular users only their own
        if user_role == UserRole.ADMIN:
            query = db.query(Expense)
        else:
            query = db.query(Expense).filter(Expense.user_id == user_id)

        if category:
            query = query.filter(Expense.category == category)  # type: ignore[arg-type]
        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        expenses = query.order_by(Expense.date.desc()).all()
        logger.info("User %s listed %s expenses", user_id, len(expenses))
        return expenses

    @staticmethod
    def create_expense(
        db: Session,
        user_id: int,
        expense: ExpenseCreate,
    ) -> Expense:
        """
        Create a new expense for the authenticated user.

        Args:
            db: Database session
            user_id: User ID to associate expense with
            expense: ExpenseCreate schema

        Returns:
            Newly created Expense object
        """
        db_expense = Expense(
            description=expense.description,
            amount=expense.amount,
            category=expense.category,
            user_id=user_id,
        )
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
        logger.info(
            "User %s created expense %s: %s (%s)",
            user_id,
            db_expense.id,
            expense.description,
            expense.amount,
        )
        return db_expense

    @staticmethod
    def get_expense_by_id(db: Session, expense_id: int) -> Optional[Expense]:
        """
        Retrieve expense by ID.

        Args:
            db: Database session
            expense_id: Expense ID

        Returns:
            Expense object or None if not found
        """
        return db.query(Expense).filter(Expense.id == expense_id).first()

    @staticmethod
    def verify_expense_access(
        db: Session, expense_id: int, user_id: int, user_role: UserRole
    ) -> Expense:
        """
        Verify user has access to expense and return it.

        Admins have access to all expenses, users only their own.

        Args:
            db: Database session
            expense_id: Expense ID to check
            user_id: Current user ID
            user_role: Current user role

        Returns:
            Expense object

        Raises:
            ResourceNotFoundException: If expense not found
            AuthorizationException: If user doesn't have access
        """
        expense = ExpenseService.get_expense_by_id(db, expense_id)
        if not expense:
            raise ResourceNotFoundException(f"Expense with id {expense_id} not found")

        if user_role != UserRole.ADMIN and expense.user_id != user_id:
            logger.warning(
                "User %s attempted unauthorized access to expense %s",
                user_id,
                expense_id,
            )
            raise AuthorizationException(
                "You don't have permission to access this expense"
            )

        return expense

    @staticmethod
    def update_expense(
        db: Session,
        expense_id: int,
        user_id: int,
        user_role: UserRole,
        expense_update: ExpenseUpdate,
    ) -> Expense:
        """
        Update an expense (verify ownership/admin).

        Args:
            db: Database session
            expense_id: Expense ID to update
            user_id: Current user ID
            user_role: Current user role
            expense_update: ExpenseUpdate schema

        Returns:
            Updated Expense object

        Raises:
            ResourceNotFoundException: If expense not found
            AuthorizationException: If user doesn't have access
        """
        expense = ExpenseService.verify_expense_access(
            db, expense_id, user_id, user_role
        )

        if expense_update.description is not None:
            expense.description = expense_update.description  # type: ignore[assignment]
        if expense_update.amount is not None:
            expense.amount = expense_update.amount  # type: ignore[assignment]
        if expense_update.category is not None:
            expense.category = expense_update.category  # type: ignore[assignment]

        db.commit()
        db.refresh(expense)
        logger.info("User %s updated expense %s", user_id, expense_id)
        return expense

    @staticmethod
    def delete_expense(
        db: Session,
        expense_id: int,
        user_id: int,
        user_role: UserRole,
    ) -> None:
        """
        Delete an expense (verify ownership/admin).

        Args:
            db: Database session
            expense_id: Expense ID to delete
            user_id: Current user ID
            user_role: Current user role

        Raises:
            ResourceNotFoundException: If expense not found
            AuthorizationException: If user doesn't have access
        """
        expense = ExpenseService.verify_expense_access(
            db, expense_id, user_id, user_role
        )
        db.delete(expense)
        db.commit()
        logger.info("User %s deleted expense %s", user_id, expense_id)

    @staticmethod
    def get_total_spent_by_user(
        db: Session,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> float:
        """
        Calculate total spending for a user in a period.

        Args:
            db: Database session
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            Total amount spent
        """
        query = db.query(Expense).filter(Expense.user_id == user_id)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        total = sum(expense.amount for expense in query.all())
        return float(total)
