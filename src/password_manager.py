from passlib.context import CryptContext
from jose import jwt, JWTError
from src.config import ALGORITHM, SECRET_KEY

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def decode_jwt_token(token: str) -> dict:
    """Decode and return the payload of a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise Exception("Invalid authentication credentials") from e