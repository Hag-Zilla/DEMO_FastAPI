#!/bin/bash

# Function to run commands and handle errors
run_command() {
    local cmd="$1"
    echo "Exécution : $cmd"
    # Exécuter la commande et capturer stderr
    output=$($cmd 2>&1)
    exit_code=$?
    # Vérifier le code de sortie
    if [ $exit_code -ne 0 ]; then
        echo "Erreur : la commande '$cmd' a échoué avec le code de sortie : $exit_code"
        echo "Message d'erreur : $output"
        exit $exit_code
    fi
    # Afficher la sortie standard si nécessaire
    echo "$output"
}

# Update system packages
run_command "sudo apt-get update"

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
    run_command "conda env create --file=$ENV_FILE"

    # Initialize Conda
    run_command "conda init"

    # Reload the shell to apply changes made by conda init
    echo "Reloading the shell..."
    if [ "$SHELL" = "/bin/zsh" ]; then
        source ~/.zshrc
    else
        source ~/.bashrc
    fi

    # Activate the environment
    conda activate "$ENV_NAME"

    # Upgrade pip
    run_command "pip install --upgrade pip"

    # Install dependencies from requirements.txt
    run_command "pip install -r requirements.txt"

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
    run_command "pyenv install -s $PYTHON_VERSION"

    # Set the local Python version for the project
    run_command "pyenv local $PYTHON_VERSION"

    # Create the venv environment
    run_command "python -m venv --prompt $ENV_NAME venv"

    # Activate the environment
    source ./venv/bin/activate

    # Upgrade pip
    run_command "pip install --upgrade pip"

    # Install dependencies from requirements.txt
    run_command "pip install -r requirements.txt"

    echo "The venv environment 'venv' has been created successfully."
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