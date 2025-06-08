from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.config import ALGORITHM, SECRET_KEY
from src.database.database import get_db
from src.database.models import User as UserModel
from src.password_manager import get_password_hash
from src.response_manager import ResponseManager

from jose import jwt, JWTError

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

################### PYDANTIC MODELS ###################

class UserSchema(BaseModel):
    username: str = Field(..., description="The unique username of the user", example="john_doe")
    password: str = Field(..., description="The password for the user account", example="secure_password123")
    budget: float = Field(..., description="The budget allocated to the user", example=1000.0)
    role: str = Field(None, description="The updated role of the user (optional)", example="user")
    disabled: bool = Field(False, description="Indicates if the user account is disabled", example=False)

    model_config = {"from_attributes": True}

################### FUNCTIONS ###################

def decode_jwt_token(token: str) -> dict:
    """Decode and return the payload of a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[Session, Depends(get_db)]
                           ) -> UserModel:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"},
                                          )
    try:
        payload = decode_jwt_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if user is None:
            raise credentials_exception
        if user.disabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user  # Return the SQLAlchemy model instance directly

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

def is_admin(current_user: Annotated[UserModel, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user


################### ROUTES ###################

@router.post("/create", name="Create User")
async def create_user(user: UserSchema, db: Annotated[Session, Depends(get_db)]):
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        hashed_password=hashed_password,
        budget=user.budget,
        role="user",  # Force role to 'user' regardless of input
        disabled=user.disabled
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "budget": db_user.budget, "role": db_user.role, "disabled": db_user.disabled}

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

@router.put("/update/", responses=ResponseManager.responses, name="Self Update User")
async def self_update_user(
    user_update: UserSchema,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[UserModel, Depends(get_current_user)]
):
    user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
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

@router.put("/update/{user_id}/", responses=ResponseManager.responses, name="Admin Update User")
async def admin_update_user(
    user_id: int,
    user_update: UserSchema,
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[UserModel, Depends(is_admin)]
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = user_update.username
    user.budget = user_update.budget
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

@router.delete("/delete/{user_id}/", responses=ResponseManager.responses, name="Delete User")
async def delete_user(user_id: int,db: Annotated[Session, Depends(get_db)],
                      admin: Annotated[UserModel, Depends(is_admin)]
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with id {user_id} has been deleted."}

# @router.get("/test/", responses=ResponseManager.responses, name="test User")
# async def test_user(
#     db: Annotated[Session, Depends(get_db)],
#     current_user: Annotated[User, Depends(get_current_user)],
#     user_id: int = Query(description="Put the user ID")
# ):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     db.delete(user)
#     db.commit()
#     return {"message": f"User with id {user_id} has been deleted."}