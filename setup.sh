#!/bin/bash
#
# Setup Script - Initialize Development Environment
#
# This script sets up a complete Python development environment for DEMO_FastAPI.
# It handles multiple environment managers (uv, venv, conda, pipenv) and runs
# the admin bootstrap process to create initial database and admin user.
#
# Usage:
#   bash setup.sh        # Interactive setup
#   uv venv && uv sync   # Manual uv setup
#   python -m venv venv  # Manual venv setup
#
# =============================================================================
# CONFIGURATION
# =============================================================================

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

# =============================================================================
# PRIVATE HELPERS
# =============================================================================

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

# =============================================================================
# PUBLIC FUNCTIONS
# =============================================================================

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
    # If .venv exists, offer to remove and recreate to avoid uv failing with existing env
    if [ -d ".venv" ]; then
        echo ".venv already exists."
        read -r -p "Remove and recreate .venv? (y/n): " recreate
        if [ "${recreate,,}" = "y" ]; then
            run_command "rm -rf .venv"
        else
            echo "Keeping existing .venv. If you want a fresh env, remove .venv and re-run setup."
        fi
    fi

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

    # Allow specifying a Python version for the venv.
    # Preference order: .python-version -> pyproject requires-python -> user prompt -> system python
    local desired_version=""
    if [ -n "${PYTHON_VERSION:-}" ]; then
        desired_version="$PYTHON_VERSION"
        echo "Requested Python version for venv: $desired_version"
    else
        read -r -p "Specify Python version for venv (e.g. 3.11). Leave empty to use system python3: " desired_version
    fi

    local python_bin=""
    if [ -n "$desired_version" ]; then
        # Try to locate a matching interpreter on PATH (e.g. python3.11)
        if command -v "python$desired_version" &> /dev/null; then
            python_bin=$(command -v "python$desired_version")
        elif command -v "python${desired_version%.*}" &> /dev/null; then
            python_bin=$(command -v "python${desired_version%.*}")
        fi

        if [ -n "$python_bin" ]; then
            # Verify the interpreter's major.minor
            det_ver=$($python_bin -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || true)
            if [ -n "$det_ver" ] && [[ "$det_ver" != "${desired_version%.*}" && "$det_ver" != "$desired_version" ]]; then
                echo "Found interpreter $python_bin but version $det_ver does not match requested $desired_version"
                read -r -p "Use it anyway? (y/n): " use_anyway
                if [ "${use_anyway,,}" != "y" ]; then
                    python_bin=""
                fi
            fi
        fi

        if [ -z "$python_bin" ]; then
            echo "Could not find Python $desired_version on PATH."
            read -r -p "Continue with system python3 instead? (y to continue with system, n to abort): " cont
            if [ "${cont,,}" = "y" ]; then
                if command -v python3 &> /dev/null; then
                    python_bin=python3
                elif command -v python &> /dev/null; then
                    python_bin=python
                else
                    echo "No system python found. Aborting."
                    exit 1
                fi
            else
                echo "Aborting setup."
                exit 1
            fi
        fi
    else
        if command -v python3 &> /dev/null; then
            python_bin=python3
        elif command -v python &> /dev/null; then
            python_bin=python
        else
            echo "Python is not installed. Please install Python and retry."
            exit 1
        fi
    fi

    # Create the venv environment using the selected interpreter
    run_command "$python_bin -m venv --prompt $ENV_NAME venv"

    # Activate the environment
    # shellcheck source=/dev/null
    source ./venv/bin/activate || { echo "Error: Failed to activate venv."; exit 1; }

    # Upgrade pip
    run_command "pip install --upgrade pip"

    # Install dependencies from requirements.txt (preferred) or generate it from uv.lock
    if [ -f "requirements.txt" ]; then
        run_command "pip install -r requirements.txt"
    elif [ -f "uv.lock" ] && command -v uv &> /dev/null; then
        echo "uv.lock found and uv available — attempting to export requirements.txt from lock"
        # Try a couple of common uv export invocations
        if uv export -f requirements.txt >/dev/null 2>&1; then
            run_command "uv export -f requirements.txt"
            run_command "pip install -r requirements.txt"
        elif uv export --format=requirements.txt -o requirements.txt >/dev/null 2>&1; then
            run_command "uv export --format=requirements.txt -o requirements.txt"
            run_command "pip install -r requirements.txt"
        else
            echo "uv export to requirements.txt failed. Please run 'make export-reqs' or 'uv export' manually." 
            if [ -f "pyproject.toml" ]; then
                echo "Falling back to editable install from pyproject.toml"
                run_command "pip install -e ."
            else
                echo "Warning: no pyproject.toml found. Skipping dependency install."
            fi
        fi
    elif [ -f "pyproject.toml" ]; then
        run_command "pip install -e ."
    else
        echo "Warning: no requirements.txt, uv.lock, or pyproject.toml found. Skipping dependency install."
    fi

    run_admin_bootstrap

    echo "The venv environment 'venv' has been created successfully."
}

# =============================================================================
# COMMAND LINE INTERFACE
# =============================================================================

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
PROJECT_NAME=$(echo "${PROJECT_RAW_NAME:-demo-fastapi}" | sed 's/[-_]/ /g' | tr '[:lower:]' '[:upper:]')
if [ -z "${PROJECT_NAME:-}" ]; then
    PROJECT_NAME="DEMO FASTAPI"
fi

# Print setup report
echo ""
echo "████████████████████████████████████████████████████████████████"
echo "█                         SETUP REPORT                         █"
echo "████████████████████████████████████████████████████████████████"
echo ""
echo "Setup Status: COMPLETED"
echo ""

if [ "${SETUP_WARNINGS+set}" = "set" ] && [ "${#SETUP_WARNINGS[@]}" -gt 0 ]; then
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
