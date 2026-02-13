#!/bin/bash

set -euo pipefail

# Function to run commands and handle errors
run_command() {
    local cmd="$1"
    echo "Executing : $cmd"
    # Execute the command and capture stderr
    output=$(eval "$cmd" 2>&1)
    exit_code=$?
    # Check the exit code
    if [ "$exit_code" -ne 0 ]; then
        if echo "$output" | grep -q "warning"; then
            echo "Warning : the command '$cmd' generated a warning with exit code : $exit_code"
            echo "Warning message : $output"
        else
            echo "Error : the command '$cmd' failed with exit code : $exit_code"
            echo "Error message : $output"
            exit $exit_code
        fi
    fi
    # Display the standard output if necessary
    echo "$output"
}

# Update system packages
run_command "sudo apt-get update"

# Path to the environment.yml file
ENV_FILE="environment.yml"

# Check if environment.yml exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: $ENV_FILE not found."
    exit 1
fi

# Function to extract values from environment.yml
extract_value() {
    local key="$1"
    grep "^$key:" "$ENV_FILE" | sed "s/^$key: //"
}

# Extract the environment name and Python version from environment.yml
ENV_NAME=$(extract_value "name")
FULL_PYTHON_VERSION=$(grep -A 1 "^dependencies:" "$ENV_FILE" | grep "python=" | sed "s/.*python=//")
# Extract major.minor version (e.g., 3.9, 3.10, 3.11, 3.12.1 -> 3.12)
PYTHON_VERSION=$(echo "$FULL_PYTHON_VERSION" | sed -E 's/^([0-9]+\.[0-9]+).*/\1/')

# Function to create a Conda environment
create_conda_env() {
    # Check if Conda is installed
    if ! command -v conda &> /dev/null
    then
        echo "Conda is not installed. Please install Conda before proceeding."
        exit 1
    fi
    
    # Create the Conda environment
    run_command "conda env create --file=$ENV_FILE"

    # Initialize Conda for the current shell
    if [ -n "$ZSH_VERSION" ]; then
        eval "$(conda shell.zsh hook)"
    elif [ -n "$BASH_VERSION" ]; then
        eval "$(conda shell.bash hook)"
    else
        # Fallback: try to detect from SHELL variable
        if [[ "$SHELL" == *"zsh"* ]]; then
            eval "$(conda shell.zsh hook)"
        else
            eval "$(conda shell.bash hook)"
        fi
    fi

    # Activate the environment
    conda activate "$ENV_NAME" || { echo "Error: Failed to activate conda environment."; exit 1; }

    # Upgrade pip (optional, but recommended)
    run_command "pip install --upgrade pip"

    echo "The Conda environment '$ENV_NAME' has been created successfully."
    echo "All dependencies have been installed from environment.yml"
}

# Function to create a venv environment using pyenv
create_venv_env() {
    # Check if pyenv is installed
    if ! command -v pyenv &> /dev/null
    then
        echo "pyenv is not installed. Please install pyenv before proceeding."
        exit 1
    fi

    # Check if venv directory already exists
    if [ -d "venv" ]; then
        echo "Warning: venv directory already exists."
        read -r -p "Do you want to remove it and create a new one? (y/n): " confirm
        if [ "${confirm,,}" = "y" ]; then
            rm -rf venv
        else
            echo "Aborting setup."
            exit 0
        fi
    fi

    # Install the specified Python version using pyenv
    run_command "pyenv install -s $PYTHON_VERSION"

    # Set the local Python version for the project
    run_command "pyenv local $PYTHON_VERSION"

    # Create the venv environment
    run_command "python -m venv --prompt $ENV_NAME venv"

    # Activate the environment
    # shellcheck source=/dev/null
    source ./venv/bin/activate || { echo "Error: Failed to activate venv."; exit 1; }

    # Upgrade pip
    run_command "pip install --upgrade pip"

    # Install dependencies from requirements.txt
    if [ -f "requirements.txt" ]; then
        run_command "pip install -r requirements.txt"
    else
        echo "Warning: requirements.txt not found. Skipping pip install."
    fi

    echo "The venv environment 'venv' has been created successfully."
}

# Ask the user which environment manager to use
echo "Which environment manager would you like to use? (conda/venv)"
read -r ENV_MANAGER

# Convert to lowercase for case-insensitive comparison
ENV_MANAGER_LOWER=$(echo "$ENV_MANAGER" | tr '[:upper:]' '[:lower:]')

if [ "$ENV_MANAGER_LOWER" = "conda" ]; then
    create_conda_env
elif [ "$ENV_MANAGER_LOWER" = "venv" ]; then
    create_venv_env
else
    echo "Invalid choice. Please choose either 'conda' or 'venv'."
    exit 1
fi