from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Centralized configuration variables
SECRET_KEY = os.getenv("SECRET_KEY", "your_default_secret_key")  # Default
ALGORITHM = os.getenv("ALGORITHM")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 30))  # Default to 30 minutes