from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.database.models import User
from src.password_manager import get_password_hash, verify_password
from src.authentication_manager import get_current_user
from pydantic import BaseModel
from src.database.database import get_db
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from src.response_manager import ResponseManager

router = APIRouter()

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class UserCreate(BaseModel):
    username: str
    password: str
    budget: float

@router.post("/", responses=ResponseManager.responses, name="Create User", tags=["User Management"])
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, budget=user.budget)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"username": db_user.username, "budget": db_user.budget}

@router.post("/token", name="Login", tags=["User Management"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", name="Get Current User", tags=["User Management"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/budget/", responses=ResponseManager.responses, name="Update Budget", tags=["Budget Management"])
async def update_budget(new_budget: float, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update the global monthly budget for the authenticated user."""
    current_user.budget = new_budget
    db.commit()
    db.refresh(current_user)
    return {"message": "Budget updated successfully", "new_budget": current_user.budget}