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

# Project metadata source (uv/venv compatible)
PYPROJECT_FILE="pyproject.toml"

# Function to extract simple quoted values from pyproject.toml
extract_pyproject_value() {
    local key="$1"
    if [ -f "$PYPROJECT_FILE" ]; then
        grep -E "^$key\s*=\s*\".*\"" "$PYPROJECT_FILE" | head -n 1 | sed -E 's/^[^=]+=\s*"(.*)"/\1/'
    fi
}

# Derive environment/project name and Python version hints.
PROJECT_RAW_NAME=$(extract_pyproject_value "name")
ENV_NAME=$(echo "${PROJECT_RAW_NAME:-demo-fastapi}" | tr '-' '_')

PYTHON_VERSION=""
if [ -f ".python-version" ]; then
    PYTHON_VERSION=$(head -n 1 .python-version | tr -d '[:space:]')
elif [ -f "$PYPROJECT_FILE" ]; then
    REQUIRES_PYTHON=$(extract_pyproject_value "requires-python")
    # Pick the first major.minor found (e.g. >=3.11,<3.14 -> 3.11)
    PYTHON_VERSION=$(echo "$REQUIRES_PYTHON" | sed -nE 's/.*([0-9]+\.[0-9]+).*/\1/p' | head -n 1)
fi

# Run admin bootstrap script as part of installation
run_admin_bootstrap() {
    if [ -f "project_spec.sh" ]; then
        echo "Launching admin bootstrap (project_spec.sh)..."
        bash project_spec.sh
    else
        echo "Warning: project_spec.sh not found. Skipping admin bootstrap."
    fi
}

# Function to create a uv environment
create_uv_env() {
    # Check if uv is installed
    if ! command -v uv &> /dev/null
    then
        echo "uv is not installed. Attempting auto-install..."
        run_optional_command "curl -LsSf https://astral.sh/uv/install.sh | sh"
        export PATH="$HOME/.local/bin:$PATH"
        if ! command -v uv &> /dev/null; then
            echo "uv install failed. Please install it manually and retry."
            echo "Install command: curl -LsSf https://astral.sh/uv/install.sh | sh"
            exit 1
        fi
    fi

    # Create uv virtual environment (default .venv). Request python version if available.
    if [ -n "${PYTHON_VERSION:-}" ]; then
        run_command "uv venv --python $PYTHON_VERSION"
    else
        run_command "uv venv"
    fi

    # Install dependencies into the uv environment
    if [ -f "pyproject.toml" ]; then
        run_command "uv sync"
    elif [ -f "requirements.txt" ]; then
        run_command "uv pip install -r requirements.txt"
    else
        echo "Warning: no pyproject.toml or requirements.txt found. Skipping dependency install."
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

    local python_bin=""
    if command -v python3 &> /dev/null; then
        python_bin="python3"
    elif command -v python &> /dev/null; then
        python_bin="python"
    else
        echo "Python is not installed. Please install Python and retry."
        exit 1
    fi

    # Create the venv environment
    run_command "$python_bin -m venv --prompt $ENV_NAME venv"

    # Activate the environment
    # shellcheck source=/dev/null
    source ./venv/bin/activate || { echo "Error: Failed to activate venv."; exit 1; }

    # Upgrade pip
    run_command "pip install --upgrade pip"

    # Install dependencies from requirements.txt
    if [ -f "requirements.txt" ]; then
        run_command "pip install -r requirements.txt"
    elif [ -f "pyproject.toml" ]; then
        run_command "pip install -e ."
    else
        echo "Warning: no requirements.txt or pyproject.toml found. Skipping dependency install."
    fi

    run_admin_bootstrap

    echo "The venv environment 'venv' has been created successfully."
}

# Ask the user which environment manager to use
echo "Which environment manager would you like to use? [uv/venv] (default: uv)"
read -r ENV_MANAGER

# Convert to lowercase for case-insensitive comparison
ENV_MANAGER_LOWER=$(echo "$ENV_MANAGER" | tr '[:upper:]' '[:lower:]')
if [ -z "$ENV_MANAGER_LOWER" ]; then
    ENV_MANAGER_LOWER="uv"
fi

if [ "$ENV_MANAGER_LOWER" = "venv" ]; then
    create_venv_env
elif [ "$ENV_MANAGER_LOWER" = "uv" ]; then
    create_uv_env
else
    echo "Invalid choice. Please choose 'venv' or 'uv'."
    exit 1
fi

# Extract project name from pyproject.toml when present
PROJECT_NAME=$(echo "${PROJECT_RAW_NAME:-demo-fastapi}" | tr '-_' '  ' | sed 's/.*/\U&/')
if [ -z "${PROJECT_NAME:-}" ]; then
    PROJECT_NAME="DEMO FASTAPI"
fi

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
