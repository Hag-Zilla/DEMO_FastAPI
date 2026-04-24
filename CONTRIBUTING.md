# 🤝 Contributing to DEMO_FastAPI

Thank you for your interest in contributing to DEMO_FastAPI! This document explains how to contribute code to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Contribution Workflow](#contribution-workflow)
- [Making Changes](#making-changes)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

## Getting Started

### Prerequisites

- **Python 3.14+**
- **Git**
- **uv** (modern Python package manager) — [Installation](https://docs.astral.sh/uv/getting-started/)

### Fork & Clone

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR_USERNAME/DEMO_FastAPI.git
cd DEMO_FastAPI

# Add upstream remote for keeping in sync
git remote add upstream https://github.com/Hag-Zilla/DEMO_FastAPI.git
```

## Contribution Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Use descriptive branch names like:
- `feature/add-expense-export` — for new features
- `fix/auth-token-expiry` — for bug fixes
- `docs/update-deployment-guide` — for documentation

### 2. Set Up Development Environment

```bash
# Create local env file from template (one-time)
make init-env

# Setup uv environment (.venv + runtime dependencies)
make init

# Optional: install runtime deps for API service only
make sync-api

# Install pre-commit hooks
make install-hooks
```

This will:
- Create a `.venv` Python environment with `uv` (if missing)
- Install runtime dependencies
- Install pre-commit hooks for automatic code quality checks

### 3. Make Your Changes

Edit files following the project structure and code organization. See [doc/STANDARDS.md](doc/STANDARDS.md) for code style guidelines.

### 4. Test Your Changes

```bash
# Run all tests
make test

# Run with coverage
pytest --cov=services/api --cov-report=html

# Run specific test file
pytest services/api/tests/test_auth.py -v
```

### 5. Run Quality Checks

```bash
# Run all pre-commit hooks
make run-hooks
```

This will automatically:
- Detect secrets and API keys
- Check code formatting
- Lint Python code
- Verify type hints
- Check docstring format
- And more...

**If hooks fail**: Edit files to address errors, then retry. Most issues auto-fix:

```bash
git add -A
git commit -m "Your message"
```

## Making Changes

### Database Schema Changes

If you modify a SQLAlchemy model in `services/api/database/models/`, you must also create or update an Alembic revision.

```bash
# Generate a new revision after changing models
make migrate-create MSG="describe schema change"

# Apply migrations locally to verify the revision
make migrate
```

Do not merge ORM model changes without the matching Alembic migration file.

### Code Organization

Follow the existing structure in [doc/STANDARDS.md](doc/STANDARDS.md):
- Type hints on all public functions
- Google-style docstrings with Args, Returns, Raises, Example
- Clear variable naming
- Organized imports

### Example Code Style

```python
def validate_expense(amount: float, category: ExpenseCategory) -> bool:
    """
    Validate that an expense is valid.

    Args:
        amount: The expense amount in dollars (must be > 0).
        category: The expense category (must be valid enum).

    Returns:
        True if valid, False otherwise.

    Raises:
        ValueError: If amount is zero or negative.

    Example:
        >>> validate_expense(50.0, ExpenseCategory.FOOD)
        True
    """
    if amount <= 0:
        raise ValueError(f"Amount must be positive, got {amount}")
    return category in ExpenseCategory
```

## Commit Message Guidelines

Use semantic commit messages with the following format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation updates
- **style**: Code style (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without feature changes
- **test**: Test additions or updates
- **chore**: Build, CI, dependency updates

### Examples

```
feat(expenses): add bulk import from CSV

- Parse CSV file with expense data
- Validate each row before inserting
- Return summary of imported/failed items

Closes #42
```

```
fix(auth): prevent token reuse after logout

Reset auth tokens on user logout to prevent
security issue with token reuse.

Fixes #98
```

## Pull Request Process

### 1. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 2. Open a Pull Request on GitHub

**PR Title**: Clear, concise description
**PR Description**: Explain what changed and why

Example:

```markdown
## Description
Adds CSV import functionality for bulk expense uploads.

## Type of Change
- [x] New feature
- [ ] Bug fix
- [ ] Documentation update

## Testing
- Run: `make test`
- Tested with: Sample CSV file with 100 expenses
- All tests pass ✓

## Checklist
- [x] Tests pass locally (`make test`)
- [x] Pre-commit hooks pass (`make run-hooks`)
- [x] Code follows style guidelines
- [x] Docstrings added/updated
- [x] Related issues linked
```

### 3. Code Review

- **Maintainers** will review your PR within a few days
- **Feedback**: Address any review comments
- **Approval**: Typically one approval required
- **Merge**: Maintainers will merge once approved

### 4. After Merge

Your changes will be:
- ✅ Merged to `main` or `dev` branch
- ✅ Tested on CI/CD pipeline
- ✅ Ready for next release

---

## For More Information

For detailed technical information about code standards, pre-commit hooks, and development tools, see:
- **[doc/DEVELOPMENT.md](doc/DEVELOPMENT.md)** — Development environment, pre-commit hooks, Makefile, troubleshooting
- **[doc/STANDARDS.md](doc/STANDARDS.md)** — Code conventions, naming, docstrings, type hints

---

**Thank you for contributing! 🙏**
