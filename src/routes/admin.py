from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database.models import User
from src.response_manager import ResponseManager
from pydantic import BaseModel
from src.database.database import get_db
from src.authentication_manager import get_current_user

router = APIRouter()

class UserUpdate(BaseModel):
    username: str
    budget: float

@router.put("/users/{user_id}/", responses=ResponseManager.responses, name="Update User")
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_update.username
    user.budget = user_update.budget
    db.commit()
    db.refresh(user)
    return {"user_id": user.id, "username": user.username, "budget": user.budget}

@router.delete("/users/{user_id}/", responses=ResponseManager.responses, name="Delete User")
async def delete_user(user_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}