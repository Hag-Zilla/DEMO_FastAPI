"""User management route handlers."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from src.database.database import get_db
from src.database.models import User as UserModel
from src.auth_manager import get_password_hash
from src.schemas import UserSchema, UserUpdateSchema
from src.auth_manager import get_current_user, is_admin

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

################### ROUTES ###################

@router.post("/create", name="Create User")
async def create_user(user: UserSchema, db: Annotated[Session, Depends(get_db)]):
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        budget=user.budget,
        role="user",  # Force role to 'user' regardless of input
        disabled=False  # Default to not disabled
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {
        "username": db_user.username,
        "budget": db_user.budget,
        "role": db_user.role,
        "disabled": db_user.disabled,
    }

@router.get("/me", name="Read Current User")
async def read_users_me(current_user: Annotated[UserModel, Depends(get_current_user)]):
    # Return a sanitized user response (do not expose hashed_password)
    return {
        "id": current_user.id,
        "username": current_user.username,
        "budget": current_user.budget,
        "role": current_user.role,
        "disabled": current_user.disabled
    }

@router.put("/update/", name="Self Update User")
async def self_update_user(
    user_update: UserSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Check if the new username is already taken by another user
    if user_update.username and user_update.username != user.username:
        existing_user = db.query(UserModel).filter(UserModel.username == user_update.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
    user.username = user_update.username
    user.budget = user_update.budget
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    # Do not allow self-update of role or disabled
    db.commit()
    db.refresh(user)
    return {
        "user_id": user.id,
        "username": user.username,
        "budget": user.budget,
        "role": user.role,
        "disabled": user.disabled
    }

@router.put("/update/{user_id}/", name="Admin Update User")
async def admin_update_user(
    user_id: int,
    user_update: UserUpdateSchema,  # <-- use the new schema
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[UserModel, Depends(is_admin)]
):
    del _admin
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.username is not None:
        # Check for unique username
        existing_user = db.query(UserModel).filter(UserModel.username == user_update.username, UserModel.id != user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = user_update.username
    if user_update.budget is not None:
        user.budget = user_update.budget
    if user_update.disabled is not None:
        user.disabled = user_update.disabled
    if user_update.password:
        user.hashed_password = get_password_hash(user_update.password)
    if user_update.role is not None:
        user.role = user_update.role
    db.commit()
    db.refresh(user)
    return {
        "user_id": user.id,
        "username": user.username,
        "budget": user.budget,
        "role": user.role,
        "disabled": user.disabled
    }

@router.delete("/delete/{user_id}/", name="Delete User")
async def delete_user(user_id: int,db: Annotated[Session, Depends(get_db)],
                      _admin: Annotated[UserModel, Depends(is_admin)]
):
    del _admin
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}