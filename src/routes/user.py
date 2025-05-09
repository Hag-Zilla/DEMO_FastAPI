from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.config import ALGORITHM, SECRET_KEY
from src.database.database import get_db
from src.database.models import User
from src.password_manager import get_password_hash
from src.response_manager import ResponseManager

from jose import jwt, JWTError

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

################### PYDANTIC MODELS ###################

class UserCreate(BaseModel):
    username: str = Field(..., description="The unique username of the user", example="john_doe")
    password: str = Field(..., description="The password for the user account", example="secure_password123")
    budget: float = Field(..., description="The budget allocated to the user", example=1000.0)

class UserUpdateWithRole(BaseModel):
    username: str = Field(..., description="The updated username of the user", example="jane_doe")
    budget: float = Field(..., description="The updated budget for the user", example=1500.0)
    role: str = Field(None, description="The updated role of the user (optional)", example="admin")

# Define a sanitized user response model
class UserResponse(BaseModel):
    id: int
    username: str
    budget: float
    role: str

    class Config:
        orm_mode = True
        from_attributes = True

################### FUNCTIONS ###################

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[Session, Depends(get_db)]) -> UserResponse:
    """Retrieve the current authenticated user based on the token."""
    try:
        print(f"Token received: {token}")  # Debug: Print the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Payload decoded: {payload}")  # Debug: Print the payload
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        print(f"JWT Error: {e}")  # Debug: Print the error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserResponse.from_orm(user)

def is_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action."
        )
    return current_user


################### ROUTES ###################

@router.post("/create", name="Create User")
async def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, budget=user.budget, role="user")  # Role is automatically set to 'user'
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "budget": db_user.budget, "role": db_user.role}

@router.get("/me", name="Read Current User")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.put("/update/{user_id}/", responses=ResponseManager.responses, name="Update User")
async def update_user(
    user_id: int,
    user_update: UserUpdateWithRole,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
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
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)], current_user: Annotated[User, Depends(get_current_user)]):
    user = db.query(User).filter(User.id == user_id).first()
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