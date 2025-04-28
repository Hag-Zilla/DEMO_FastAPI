from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Centralized configuration variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 30))  # Default to 30 minutes