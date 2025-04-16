from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import User
from src.response_manager import ResponseManager
from src.utils import get_current_user
from pydantic import BaseModel
from database import get_db

router = APIRouter()

class AlertResponse(BaseModel):
    user_id: int
    username: str
    budget: float
    total_expenses: float
    alert: str

@router.get("/", responses=ResponseManager.responses, name="Get Alerts", tags=["Alerts"])
async def get_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    alerts = []
    for user in users:
        total_expenses = sum(expense.amount for expense in user.expenses)
        if total_expenses > user.budget:
            alerts.append({
                "user_id": user.id,
                "username": user.username,
                "budget": user.budget,
                "total_expenses": total_expenses,
                "alert": "Budget exceeded!"
            })
    return alerts