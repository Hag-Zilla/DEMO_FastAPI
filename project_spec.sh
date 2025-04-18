#!/bin/bash

# This script sets up the .env file and uses a user-provided SECRET_KEY for the project

# Prompt the user to input the SECRET_KEY
read -p "Enter your SECRET_KEY: " SECRET_KEY

# Create the .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file..."
  echo "SECRET_KEY=$SECRET_KEY" > .env
  echo ".env file created with the provided SECRET_KEY."
else
  echo ".env file already exists. No changes made."
fi