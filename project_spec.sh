#!/bin/bash

# This script sets up the .env file and uses a user-provided SECRET_KEY for the project

# Add ADM_SECRET_KEY to the .env file
read -p "Enter your ADM_SECRET_KEY for the admin account: " ADM_SECRET_KEY

# Append ADM_SECRET_KEY to the .env file
if [ ! -f .env ]; then
  echo "Creating .env file..."
  echo "ADM_SECRET_KEY=$ADM_SECRET_KEY" >> .env
  echo ".env file created with the provided ADM_SECRET_KEY."
else
  echo "ADM_SECRET_KEY=$ADM_SECRET_KEY" >> .env
  echo "ADM_SECRET_KEY added to the existing .env file."
fi

# Create the admin user in the database
python <<EOF
from src.database.database import SessionLocal
from src.database.models import User
from src.password_manager import get_password_hash
import os

admin_password = os.getenv("ADM_SECRET_KEY")
if not admin_password:
    raise ValueError("ADM_SECRET_KEY is not set in the .env file.")

db = SessionLocal()
admin_user = db.query(User).filter(User.username == "admin").first()
if not admin_user:
    admin_user = User(
        username="admin",
        hashed_password=get_password_hash(admin_password),
        budget=0.0,
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    print("Admin user created with username: admin")
else:
    print("Admin user already exists.")
db.close()
EOF