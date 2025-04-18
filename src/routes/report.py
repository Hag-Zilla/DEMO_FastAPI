from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.models import Expense
from src.database.models import User
from src.response_manager import ResponseManager
from pydantic import BaseModel
from datetime import date
from src.database.database import get_db
from src.authentication_manager import get_current_user

router = APIRouter()

class PeriodReportRequest(BaseModel):
    start_date: date
    end_date: date

@router.get("/monthly/{user_id}/", responses=ResponseManager.responses, name="Monthly Report")
async def get_monthly_report(user_id: int, month: int, year: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this report.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date.between(f"{year}-{month:02d}-01", f"{year}-{month:02d}-31")
    ).all()
    report = {
        "user_id": user.id,
        "username": user.username,
        "month": month,
        "year": year,
        "expenses": [
            {"description": e.description, "amount": e.amount, "category": e.category, "date": e.date}
            for e in expenses
        ]
    }
    return report

@router.get("/period/{user_id}/", responses=ResponseManager.responses, name="Period Report")
async def get_period_report(user_id: int, report_request: PeriodReportRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    expenses = db.query(Expense).filter(
        Expense.user_id == user_id,
        Expense.date.between(report_request.start_date, report_request.end_date)
    ).all()
    report = {
        "user_id": user.id,
        "username": user.username,
        "start_date": report_request.start_date,
        "end_date": report_request.end_date,
        "expenses": [
            {"description": e.description, "amount": e.amount, "category": e.category, "date": e.date}
            for e in expenses
        ]
    }
    return report

@router.get("/all/", responses=ResponseManager.responses, name="All Users Reports")
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