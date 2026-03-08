#!/bin/bash

#!/bin/bash

# Print banners from app/utils/branding so they live outside scripts
if [ -f "app/utils/branding/mammoth.txt" ]; then
    cat app/utils/branding/mammoth.txt
    echo ""
fi

if [ -f "app/utils/branding/setup.txt" ]; then
    cat app/utils/branding/setup.txt
    echo ""
else
    echo "Initializing environment..."
    echo ""
fi

set -euo pipefail

# Arrays to track warnings
declare -a SETUP_WARNINGS

# Function to run commands and handle errors
run_command() {
    local cmd="$1"
    echo "Executing : $cmd"
    # Execute the command and capture output
    if output=$(eval "$cmd" 2>&1); then
        echo "$output"
    else
        exit_code=$?
        echo ""
        echo "====================================================="
        echo "ERROR: Command failed with exit code: $exit_code"
        echo "Command: $cmd"
        echo "Output:"
        echo "====================================================="
        echo "$output"
        echo "====================================================="
        exit $exit_code
    fi
}

# Function to run optional commands (non-fatal, logs warnings)
run_optional_command() {
    local cmd="$1"
    echo "Executing (optional) : $cmd"
    # Try to run the command, capturing output and handling failures gracefully
    if output=$(eval "$cmd" 2>&1); then
        echo "$output"
    else
        SETUP_WARNINGS+=("Command '$cmd' was skipped (non-critical)")
        echo "⚠️  Warning: $cmd was skipped (non-fatal)"
    fi
}

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

# Run admin bootstrap script as part of installation
run_admin_bootstrap() {
    if [ -f "project_spec.sh" ]; then
        echo "Launching admin bootstrap (project_spec.sh)..."
        bash project_spec.sh
    else
        echo "Warning: project_spec.sh not found. Skipping admin bootstrap."
    fi
}

# Function to create a Conda environment
create_conda_env() {
    # Check if Conda is installed
    if ! command -v conda &> /dev/null
    then
        echo "Conda is not installed. Please install Conda before proceeding."
        exit 1
    fi

    # Check if Conda environment already exists
    if conda env list | awk '{print $1}' | grep -Fxq "$ENV_NAME"; then
        echo "Warning: Conda environment '$ENV_NAME' already exists."
        read -r -p "Do you want to remove it and create a new one? (y/n): " confirm
        if [ "${confirm,,}" = "y" ]; then
            run_command "conda env remove -n $ENV_NAME -y"
        else
            echo "Aborting setup."
            exit 0
        fi
    fi
    
    # Create the Conda environment
    run_command "conda env create --file=$ENV_FILE"

    # Initialize Conda for the current shell
    if [ -n "${ZSH_VERSION:-}" ]; then
        eval "$(conda shell.zsh hook)"
    elif [ -n "${BASH_VERSION:-}" ]; then
        eval "$(conda shell.bash hook)"
    else
        # Fallback: try to detect from SHELL variable
        if [[ "${SHELL:-}" == *"zsh"* ]]; then
            eval "$(conda shell.zsh hook)"
        else
            eval "$(conda shell.bash hook)"
        fi
    fi

    # Activate the environment
    conda activate "$ENV_NAME" || { echo "Error: Failed to activate conda environment."; exit 1; }

    # Upgrade pip (optional, but recommended)
    run_command "pip install --upgrade pip"

    run_admin_bootstrap

    echo "The Conda environment '$ENV_NAME' has been created successfully."
    echo "All dependencies have been installed from environment.yml"
}

# Function to create a venv environment using pyenv
#
create_uv_env() {
    # Check if uv is installed
    if ! command -v uv &> /dev/null
    then
        echo "uv is not installed. Install it with: pip install uv"
        exit 1
    fi

    # Create uv virtual environment (default .venv). Request python version if available.
    if [ -n "${PYTHON_VERSION:-}" ]; then
        run_command "uv venv --python $PYTHON_VERSION"
    else
        run_command "uv venv"
    fi

    # Install dependencies into the uv environment
    if [ -f "requirements.txt" ]; then
        run_command "uv pip install -r requirements.txt"
    else
        echo "Warning: requirements.txt not found. Skipping pip install."
    fi

    # Activate the created venv for subsequent interactive steps (project_spec.sh expects python)
    if [ -f ".venv/bin/activate" ]; then
        # shellcheck source=/dev/null
        source .venv/bin/activate || { echo "Error: failed to activate .venv"; exit 1; }
    fi

    run_admin_bootstrap

    echo "The uv environment (.venv) has been created successfully."
}
create_venv_env() {
    # Check if pyenv is installed
    if ! command -v pyenv &> /dev/null
    then
        echo "pyenv is not installed. Please install pyenv before proceeding."
        exit 1
    fi
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

    run_admin_bootstrap

    echo "The venv environment 'venv' has been created successfully."
}

# Ask the user which environment manager to use
echo "Which environment manager would you like to use? (conda/venv/uv)"
read -r ENV_MANAGER

# Convert to lowercase for case-insensitive comparison
ENV_MANAGER_LOWER=$(echo "$ENV_MANAGER" | tr '[:upper:]' '[:lower:]')

if [ "$ENV_MANAGER_LOWER" = "conda" ]; then
    create_conda_env
elif [ "$ENV_MANAGER_LOWER" = "venv" ]; then
    create_venv_env
elif [ "$ENV_MANAGER_LOWER" = "uv" ]; then
    create_uv_env
else
    echo "Invalid choice. Please choose 'conda', 'venv' or 'uv'."
    exit 1
fi

# Extract project name from environment.yml if not already done
PROJECT_NAME=$(extract_value "name" | tr '_' ' ' | sed 's/.*/\U&/')

# Print setup report
echo ""
echo "████████████████████████████████████████████████████████████████"
echo "█                    ✅  SETUP REPORT  ✅                        █"
echo "████████████████████████████████████████████████████████████████"
echo ""
echo "Setup Status: COMPLETED"
echo ""

if [ ${#SETUP_WARNINGS[@]} -gt 0 ]; then
    echo "⚠️  Warnings during setup:"
    for warning in "${SETUP_WARNINGS[@]}"; do
        echo "  • $warning"
    done
    echo ""
else
    echo "✓ No warnings"
    echo ""
fi

if [ -f "app/utils/branding/completion.txt" ]; then
    # Render template to a temporary file so we `cat` a real .txt file
    tmpfile=$(mktemp)
    if sed "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" app/utils/branding/completion.txt > "$tmpfile"; then
        cat "$tmpfile"
    else
        echo "Setup completed successfully — $PROJECT_NAME is ready."
    fi
    rm -f "$tmpfile"
    echo ""
else
    echo "✓ $PROJECT_NAME is ready to use"
    echo ""
fi
