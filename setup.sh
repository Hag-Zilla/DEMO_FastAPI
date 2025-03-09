#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt update
if [ $? -ne 0 ]; then
    echo "Failed to update system packages."
    exit 1
fi

# Path to the environment.yml file
ENV_FILE="environment.yml"

# Function to extract values from environment.yml
extract_value() {
    local key=$1
    grep "^$key:" $ENV_FILE | sed "s/^$key: //"
}

# Extract the environment name and Python version from environment.yml
ENV_NAME=$(extract_value "name")
FULL_PYTHON_VERSION=$(grep -A 1 "^dependencies:" $ENV_FILE | grep "python=" | sed "s/.*python=//")
PYTHON_VERSION=${FULL_PYTHON_VERSION: -4}

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
    conda env create --file=$ENV_FILE
    if [ $? -ne 0 ]; then
        echo "Failed to create the Conda environment."
        exit 1
    fi

    # Initialize Conda
    echo "Initializing Conda..."
    conda init
    if [ $? -ne 0 ]; then
        echo "Failed to initialize Conda."
        exit 1
    fi

    # Reload the shell to apply changes made by conda init
    echo "Reloading the shell..."
    if [ "$SHELL" = "/bin/zsh" ]; then
        source ~/.zshrc
    else
        source ~/.bashrc
    fi

    # Activate the environment
    echo "Activating the Conda environment..."
    conda activate $ENV_NAME
    if [ $? -ne 0 ]; then
        echo "Failed to activate the Conda environment."
        exit 1
    fi

    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
    if [ $? -ne 0 ]; then
        echo "Failed to upgrade pip."
        exit 1
    fi

    # Install dependencies from requirements.txt
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies from requirements.txt."
        exit 1
    fi

    echo "The Conda environment '$ENV_NAME' has been created and activated successfully."
}

# Function to create a venv environment using pyenv
create_venv_env() {
    # Check if pyenv is installed
    if ! command -v pyenv &> /dev/null
    then
        echo "pyenv is not installed. Please install pyenv before proceeding."
        exit 1
    fi

    # Install the specified Python version using pyenv
    echo "Installing Python $PYTHON_VERSION using pyenv..."
    pyenv install -s $PYTHON_VERSION
    if [ $? -ne 0 ]; then
        echo "Failed to install Python $PYTHON_VERSION using pyenv."
        exit 1
    fi

    # Set the local Python version for the project
    echo "Setting local Python version to $PYTHON_VERSION..."
    pyenv local $PYTHON_VERSION
    if [ $? -ne 0 ]; then
        echo "Failed to set local Python version to $PYTHON_VERSION."
        exit 1
    fi

    # Create the venv environment
    echo "Creating the venv environment with Python $PYTHON_VERSION..."
    python -m venv --prompt $ENV_NAME venv
    if [ $? -ne 0 ]; then
        echo "Failed to create the venv environment."
        exit 1
    fi

    # Activate the environment
    echo "Activating the venv environment..."
    source ./venv/bin/activate
    if [ $? -ne 0 ]; then
        echo "Failed to activate the venv environment."
        exit 1
    fi

    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
    if [ $? -ne 0 ]; then
        echo "Failed to upgrade pip."
        exit 1
    fi

    # Install dependencies from requirements.txt
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies from requirements.txt."
        exit 1
    fi

    echo "The venv environment 'venv' has been created and activated successfully."
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