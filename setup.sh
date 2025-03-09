#!/bin/bash

# Environment name
ENV_NAME="demo_fastapi"

# Path to the environment.yml file
ENV_FILE="environment.yml"

# Function to create a Conda environment
create_conda_env() {
    # Check if Conda is installed
    if ! command -v conda &> /dev/null
    then
        echo "Conda is not installed. Please install Conda before proceeding."
        exit 1
    fi

    # Create the Conda environment
    echo "Creating the Conda environment..."
    conda env create -f $ENV_FILE

    # Activate the environment
    echo "Activating the Conda environment..."
    source activate $ENV_NAME

    echo "The Conda environment '$ENV_NAME' has been created and activated successfully."
}

# Function to create a venv environment
create_venv_env() {
    # Check if Python is installed
    if ! command -v python3 &> /dev/null
    then
        echo "Python3 is not installed. Please install Python3 before proceeding."
        exit 1
    fi

    # Create the venv environment
    echo "Creating the venv environment..."
    python3 -m venv $ENV_NAME

    # Activate the environment
    echo "Activating the venv environment..."
    source $ENV_NAME/bin/activate

    # Install dependencies from requirements.txt
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt

    echo "The venv environment '$ENV_NAME' has been created and activated successfully."
}

# Ask the user which environment manager to use
echo "Which environment manager would you like to use? (conda/venv)"
read ENV_MANAGER

if [ "$ENV_MANAGER" == "conda" ]; then
    create_conda_env
elif [ "$ENV_MANAGER" == "venv" ]; then
    create_venv_env
else
    echo "Invalid choice. Please choose either 'conda' or 'venv'."
    exit 1
fi