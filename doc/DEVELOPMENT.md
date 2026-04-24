# 🛠️ Development Guide

This guide covers development setup, code quality standards, and workflows for DEMO_FastAPI.

---

## Table of Contents

1. [Pre-commit Hooks](#pre-commit-hooks)
2. [Code Quality Standards](#code-quality-standards)
3. [Development Workflow](#development-workflow)
4. [Testing](#testing)
5. [Dependency Management](#dependency-management)
6. [Troubleshooting](#troubleshooting)

---

## Pre-commit Hooks

### Overview

This project uses **[pre-commit](https://pre-commit.com/)** to automate code quality checks before each commit. Hooks run automatically when you execute `git commit`, ensuring code meets quality and security standards before entering the repository.

### Benefits

- ✅ **Automated Validation**: Linting, formatting, and security checks run automatically
- ✅ **Prevent Bad Commits**: Catches issues before code reaches git history
- ✅ **Consistency**: All developers follow same standards
- ✅ **Early Detection**: Security vulnerabilities, syntax errors, and formatting issues caught locally
- ✅ **Auto-fix**: Simple issues (trailing whitespace, import sorting) are fixed automatically

### Installation

Pre-commit is part of the shared `tools` dependency group. Install hooks with:

```bash
# Register hooks with git
make install-hooks
# or manually: uv run --only-group tools pre-commit install
```

### Running Hooks

```bash
# Run all hooks on staged files (automatic on git commit)
git commit -m "Your message"

# Run all hooks on all files
make run-hooks
# or: uv run --only-group tools pre-commit run --all-files

# Run hooks on only staged files
make run-hooks-staged
# or: uv run --only-group tools pre-commit run

# Bypass hooks if absolutely necessary
git commit --no-verify
```

`uvx pre-commit ...` is fine for one-off manual runs, but it is not the default workflow here because `pre-commit` is already versioned in the repository's `tools` group. `uv run --only-group tools ...` stays aligned with the project's declared and locked toolchain.

### Available Hooks

| Hook | Purpose | Auto-fix | Stage |
|------|---------|----------|-------|
| **detect-secrets** | Find hardcoded secrets/API keys | No | commit |
| **check-yaml** | Validate YAML syntax (config files) | No | commit |
| **check-json** | Validate JSON syntax | No | commit |
| **check-toml** | Validate TOML syntax (pyproject.toml) | No | commit |
| **check-xml** | Validate XML syntax | No | commit |
| **check-ast** | Check Python AST is valid | No | commit |
| **check-docstring-first** | Ensure docstring before code | No | commit |
| **trailing-whitespace** | Remove trailing whitespace | **Yes** | commit |
| **end-of-file-fixer** | Fix missing newlines at EOF | **Yes** | commit |
| **mixed-line-ending** | Normalize to LF line endings | **Yes** | commit |
| **ruff** | Fast Python linter (replaces flake8) | **Yes** | commit |
| **ruff-format** | Auto-formatter (black-compatible) | **Yes** | commit |
| **mypy** | Static type checking | No | commit |
| **pydocstyle** | Check docstring format (Google style) | No | commit |
| **shellcheck** | Check bash/shell scripts | No | commit |
| **autoflake** | Remove unused imports/variables | **Yes** | commit |
| **check-merge-conflict** | Detect merge conflict markers | No | commit |

### Configuration

Hooks are configured in `.pre-commit-config.yaml`. Key settings:

```yaml
# Python version used by hooks
default_language_version:
  python: python3.14

# Security: Detect common secrets
detect-secrets:
  args: ['--baseline', '.secrets.baseline']
  exclude: ^(uv\.lock|poetry\.lock|requirements\.txt|\.env.*|\.example|.*\.jsonl.*|services/api/logs)$

# Type checking with mypy
mypy:
  entry: uv run --only-group tools mypy
  args: ['services/api']

# Docstring format (Google style)
pydocstyle:
  args: ['--convention=google']
```

### Secrets Detection

The `detect-secrets` hook prevents accidental commits of:
- API keys, tokens, passwords
- AWS/Azure/GCP credentials
- Private keys
- Authorization tokens

**Baseline file**: `.secrets.baseline` maintains allowlisted secrets that are safe to commit (e.g., test credentials in comments).

If a secret is detected:
```bash
# 1. Option A: Don't commit the secret (recommended)
git checkout services/api/file_with_secret.py

# 2. Option B: Explicitly allow (only for non-sensitive test data)
# Edit .secrets.baseline to allowlist the pattern

# 3. Option C: Force commit (last resort - avoid)
git commit --no-verify  # NOT RECOMMENDED
```

### Updating Hooks

Hooks are pinned to specific versions in `.pre-commit-config.yaml`. Update them:

```bash
# Check for new versions and update config
make update-hooks
# or: uv run --only-group tools pre-commit autoupdate

# Review changes
git diff .pre-commit-config.yaml

# Commit updates
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"
```

### Troubleshooting

**Hooks not running?**
```bash
# Reinstall hooks
make clean-hooks
make install-hooks
```

**Hook mysteriously failed?**
```bash
# Clear cache and retry
make clean-hooks
make run-hooks
```

**Need to bypass hooks temporarily?**
```bash
git commit --no-verify  # Bypasses ALL hooks
```

**Hooks too strict?**
- Edit `.pre-commit-config.yaml` to adjust args
- Exclude files with `exclude:` patterns
- Allowlist known acceptable issues

---

## Code Quality Standards

### Python Code Organization

All Python files follow this structure (see [Standards Overview](STANDARDS.md)):

```python
"""Module docstring describing file purpose."""

# ============================================================================
# IMPORTS
# ============================================================================

# Standard library imports, then third-party, then local

# ============================================================================
# CONFIGURATION / CONSTANTS
# ============================================================================

CONSTANT_NAME = "value"
_PRIVATE_CONSTANT = "value"

# ============================================================================
# PRIVATE HELPERS
# ============================================================================

def _internal_helper() -> str:
    """Internal function prefixed with underscore."""
    pass

# ============================================================================
# PUBLIC CLASSES / FUNCTIONS
# ============================================================================

class PublicClass:
    """Public class with full docstring."""
    pass

def public_function() -> str:
    """Public function with docstring."""
    pass

# ============================================================================
# MODULE SETUP / EXPORTS
# ============================================================================

__all__ = ["PublicClass", "public_function"]
```

### Docstring Format

Use [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#381-docstrings):

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief one-line description.

    Longer description if needed. Explain purpose, behavior, and side effects.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of what is returned.

    Raises:
        ValueError: When validation fails.
        TypeError: When type is incorrect.

    Example:
        >>> result = function_name("test", 123)
        >>> print(result)
        True
    """
    pass
```

### Type Hints

All public functions should have type hints:

```python
from typing import Optional, List, Dict, Union

def process_data(
    items: List[str],
    threshold: float = 0.5,
    debug: Optional[bool] = None
) -> Dict[str, int]:
    """Process items and return summary."""
    pass
```

### Linting Standards

Hooks enforce:

- **Line length**: 100 characters (configurable in `ruff` settings)
- **Imports**: Sorted and organized (stdlib → third-party → local)
- **Unused code**: Removed automatically by `autoflake`
- **Trailing whitespace**: Removed automatically
- **Line endings**: Normalized to LF (Unix-style)

---

## Development Workflow

### 1. Setup Development Environment

```bash
# Clone and enter project
git clone <repo>
cd DEMO_FastAPI

# Setup uv environment (.venv + runtime dependencies for all services)
make init

# Install pre-commit hooks
make install-hooks

# Verify setup
make run
```

### 2. Make Changes

```bash
# Create feature branch
git checkout -b feat/my-feature

# Edit files, write tests, update docs
vim services/api/routers/my_router.py
vim services/api/tests/test_my_router.py

# Format and lint (optional - hooks will catch issues)
make format
make lint
```

### 3. Commit Changes

```bash
# Stage changes
git add services/api/routers/my_router.py services/api/tests/test_my_router.py

# Commit (hooks run automatically)
git commit -m "feat: add new endpoint for feature X

- Implement endpoint handler
- Add validation logic
- Include unit tests"

# On successful commit:
# ✓ All hooks passed
# ✓ Code is formatted
# ✓ No secrets exposed
# ✓ Docstrings are valid
# → Commit created in git history
```

### 4. Test Before Push

```bash
# Run test suite
make test

# Run linter across all files
make lint

# Run hooks on all files
make run-hooks
```

### 5. Push and Create PR

```bash
git push origin feat/my-feature
# → Create PR on GitHub/GitLab
```

### Best Practices

✅ **DO**:
- Commit frequently (small, focused commits)
- Write descriptive commit messages
- Test locally before pushing
- Follow Python/standards conventions consistently
- Ask questions in PR reviews

❌ **DON'T**:
- Use `git commit --no-verify` routinely
- Commit large files (>1MB)
- Hardcode secrets/API keys
- Skip running hooks locally
- Push to main/master without PR review

---

## Testing

### Unit & Integration Tests

Run the pytest suite:

```bash
make test
```

For coverage report:

```bash
pytest --cov=services/api --cov-report=html
```

Tests use an in-memory SQLite database with transaction rollback per test for blazing-fast execution.

### Contract Testing (Schemathesis)

Auto-generated property tests against OpenAPI schema:

```bash
make contract-test
```

Tests verify that all endpoints:
- Accept documented request formats
- Return documented response status codes
- Never crash with 5xx errors

### Load Testing (Locust)

Test API performance under concurrent load:

```bash
make load-test              # Interactive web UI (http://localhost:8089)
make load-test-headless     # CI mode (20 users, 60s)
```

Scenarios run realistic user workflows — see [services/api/tests/load_tests/locustfile.py](../services/api/tests/load_tests/locustfile.py).

**Typical use cases:**
- Identify slow endpoints
- Verify caching effectiveness (alerts, reports should be fast)
- Measure max RPS before degradation
- Validate response time SLAs

---

## Troubleshooting

### Commit fails due to hooks

**Problem**: `pre-commit hook failed with exit code 1`

**Solutions**:

```bash
# 1. Run hooks locally to see exact error
make run-hooks

# 2. Many issues auto-fix - stage fixed files
git add -A
git commit -m "..."

# 3. For unfixable issues (docstring, type errors):
#    Edit files to address errors
vim services/api/file_with_error.py
git add services/api/file_with_error.py
git commit -m "..."

# 4. If stuck, bypass (NOT RECOMMENDED):
git commit --no-verify
```

### Hooks seem outdated

```bash
# Update all hooks to latest versions
make update-hooks

# Test updated hooks
make run-hooks
```

### Pre-commit installation issues

```bash
# Nuke old installation and reinstall
make clean-hooks
make install-hooks
```

### Specific hook too strict?

Edit `.pre-commit-config.yaml` to adjust:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
    - id: ruff
      args: ['--fix', '--ignore=E501']  # Add args to ignore rules
```

Then reinstall:
```bash
uv run --only-group tools pre-commit install-hooks
```

---

## Dependency Management

### Contributor (use committed lock)

If `uv.lock` is committed, install exact versions without regenerating:

```bash
make init        # Install runtime deps for all services from uv.lock
make sync-api    # Or install only the API service runtime deps
make test
make run
```

### Maintainer (update dependencies)

To update dependencies and produce a new lock:

```bash
# Edit services/api/pyproject.toml as needed, then:
make lock           # Regenerate uv.lock
git add pyproject.toml services/api/pyproject.toml uv.lock
git commit -m "chore: update dependencies"
```

> For CI or cross-platform reproducibility: `uv lock --python 3.14`

---

## Quick Reference

```bash
# Development commands
make help              # List all available commands
make init              # Setup environment (.venv + runtime deps for all services)
make sync              # Install runtime deps for all services
make sync-api          # Install runtime deps for the API service only
make sync-all          # Alias of make sync
make run               # Start dev server
make test              # Run tests
make lint              # Lint code
make format            # Format code

# Dependency management
make lock              # Regenerate uv.lock

# Pre-commit commands
make install-hooks     # Install git hooks
make run-hooks         # Test all hooks
make update-hooks      # Update to latest versions
make clean-hooks       # Clear cache
```

---

## Additional Resources

- [Pre-commit Documentation](https://pre-commit.com)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [FastAPI Development Guide](https://fastapi.tiangolo.com/tutorial/)

---

**Last Updated**: 2026-04-22
**Maintainer**: Development Team
