from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import User
from src.response_manager import ResponseManager
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class UserUpdate(BaseModel):
    username: str
    budget: float

@router.put("/users/{user_id}/", responses=ResponseManager.responses, name="Update User", tags=["Administrative"])
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_update.username
    user.budget = user_update.budget
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "username": user.username, "budget": user.budget}

@router.delete("/users/{user_id}/", responses=ResponseManager.responses, name="Delete User", tags=["Administrative"])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}

@router.get("/reports/", responses=ResponseManager.responses, name="All Users Reports", tags=["Administrative"])
async def get_all_users_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate reports for all users (admin only)."""
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource.")

    users = db.query(User).all()
    reports = []
    for user in users:
        total_expenses = sum(expense.amount for expense in user.expenses)
        reports.append({
            "user_id": user.id,
            "username": user.username,
            "total_expenses": total_expenses,
            "remaining_budget": user.budget
        })
    return reports