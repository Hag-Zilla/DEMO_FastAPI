from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from sqlalchemy.orm import Session
from src.database.models import User
from src.password_manager import get_password_hash, verify_password
from src.authentication_manager import get_current_user
from src.database.database import get_db
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from datetime import datetime, timedelta
from src.response_manager import ResponseManager
from pydantic import BaseModel, Field
from src.config import JWT_EXPIRATION_MINUTES, SECRET_KEY, ALGORITHM

router = APIRouter()

class UserCreate(BaseModel):
    username: str = Field(..., description="The unique username of the user", example="john_doe")
    password: str = Field(..., description="The password for the user account", example="secure_password123")
    budget: float = Field(..., description="The budget allocated to the user", example=1000.0)

class UserUpdateWithRole(BaseModel):
    username: str = Field(..., description="The updated username of the user", example="jane_doe")
    budget: float = Field(..., description="The updated budget for the user", example=1500.0)
    role: str = Field(None, description="The updated role of the user (optional)", example="admin")

@router.post("/create", responses=ResponseManager.responses, name="Create User")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, budget=user.budget, role="user")  # Role is automatically set to 'user'
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "budget": db_user.budget, "role": db_user.role}

@router.get("/me", name="Get Current User")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/update/{user_id}/", responses=ResponseManager.responses, name="Update User")
async def update_user(
    user_id: int,
    user_update: UserUpdateWithRole,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update username and budget
    user.username = user_update.username
    user.budget = user_update.budget

    # Update role if provided and the current user is an admin
    if user_update.role is not None:
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update roles."
            )
        user.role = user_update.role

    db.commit()
    db.refresh(user)
    return {
        "user_id": user.id,
        "username": user.username,
        "budget": user.budget,
        "role": user.role
    }

@router.delete("/delete/{user_id}/", responses=ResponseManager.responses, name="Delete User")
async def delete_user(user_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}

from fastapi import Query
@router.get("/test/", responses=ResponseManager.responses, name="test User")
async def test_user(user_id: int = Query(description="Put the user ID"), db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}