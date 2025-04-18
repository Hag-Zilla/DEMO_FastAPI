from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Centralized configuration variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"