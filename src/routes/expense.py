from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.authentication_manager import get_current_user
from src.database.database import get_db
from src.database.models import Expense, User
from src.response_manager import ResponseManager

router = APIRouter()

class ExpenseCreate(BaseModel):
    description: str
    amount: float
    category: str
    date: date = None

# Predefined expense categories
CATEGORIES = [
    "Food", "Transportation", "Housing", "Utilities", "Health", "Leisure", "Dining Out", "Clothing",
    "Education", "Travel", "Savings and Investments", "Insurance", "Entertainment", "Gifts and Donations", "Miscellaneous"
]

@router.post("/", responses=ResponseManager.responses, name="Create Expense")
async def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not expense.date:
        expense.date = date.today()
    if expense.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Allowed categories are: {', '.join(CATEGORIES)}")
    db_expense = Expense(**expense.dict(), user_id=current_user.id)
    db.add(db_expense)

    # Automatically update the remaining budget
    current_user.budget -= expense.amount
    db.commit()
    db.refresh(db_expense)
    db.refresh(current_user)

    return {"expense": db_expense, "remaining_budget": current_user.budget}

@router.put("/{expense_id}/", responses=ResponseManager.responses, name="Update Expense")
async def update_expense(expense_id: int, updated_expense: ExpenseCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update an existing expense for the authenticated user."""
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for key, value in updated_expense.dict().items():
        setattr(expense, key, value)
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}/", responses=ResponseManager.responses, name="Delete Expense")
async def delete_expense(expense_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete an existing expense for the authenticated user."""
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}

@router.put("/budget/", responses=ResponseManager.responses, name="Update Budget")
async def update_budget(new_budget: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update the global monthly budget for the authenticated user."""
    current_user.budget = new_budget
    db.commit()
    db.refresh(current_user)
    return {"message": "Budget updated successfully", "new_budget": current_user.budget}