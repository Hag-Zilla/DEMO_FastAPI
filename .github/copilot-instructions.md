## GitHub Copilot Custom Instructions — Français / English

**Purpose**: Provide suggestions consistent with repository conventions, accelerate code
writing, and assist contributors on Python, MLOps, deployment, and observability.

**Repository Type**: This repository is dedicated to Copilot customization, instruction
quality, and prompt governance.

## Language Configuration

- **Interaction language**: English — all Copilot responses and comments directed at the
  user must be in English, unless the user explicitly switches to another language.
- **Development language**: Python — all source code, docstrings, and inline comments
  must be written in English (standard convention for code).

## Instruction Priority

1. System and platform policies
2. User request in current chat
3. Global instructions in this file
4. Repository standards file: `./docs/STANDARDS.md` (when present in the target repo)
5. Path-specific instructions in `.github/instructions/`
6. Prompt templates in `.github/prompts/`

## Conflict Resolution

- Prefer the more specific rule when two rules conflict.
- If specificity is equal, prefer the most recent update with explicit rationale.
- Prefer practical and flexible guidance unless strict behavior is clearly required.

## Repository Context

- Technical Stack: Python, Docker, FastAPI, Kubernetes, Prometheus, Grafana, Loki,
  pandas, NumPy, Jupyter, SQLAlchemy, Alembic, MLflow, DVC.
- Target Audience: data scientists, ML engineers, MLOps engineers, data engineers,
  backend developers.

## Agent Behaviour

### General

- Treat this file as the authoritative style reference for agent behaviour.
- Prefer minimal, targeted changes over broad refactors.
- Each change must be independently testable or documented if a test is not applicable.

### Custom Rules (User Preferences)

- Never perform a `git commit`, `git push`, or any version control write operation on
  behalf of the user. Propose the command instead.
- Be direct and honest. Do not flatter or soften incorrect assumptions.
- Always ask clarifying questions before proceeding when a request is ambiguous,
  incomplete, or could be interpreted in multiple ways.
- When any file in the repository is created, moved, renamed, or deleted, update
  `README.md` to reflect the change before considering the task complete.
- When proposing solutions, reference industry best practices and state-of-the-art
  approaches; explain trade-offs and justify recommendations.
- In target repositories, if `./docs/STANDARDS.md` exists, treat it as a required source
  of truth for development standards and align all proposals and generated code with it.

### Repository Standards Integration

- At the start of a coding task, explicitly check whether `./docs/STANDARDS.md` exists in
  the current repository.
- If present, read and apply its rules before implementing changes.
- If a conflict appears between this file and `./docs/STANDARDS.md`, prefer the most
  specific rule; if still ambiguous, ask a clarifying question.

### Instruction and Prompt Files

- When creating a new `.instructions.md` file, use
  `.github/instructions/TEMPLATE.instructions.md` as the base.
- `applyTo` glob patterns must be specific enough to avoid unintended matches.
- Prompt files (`.prompt.md`) must include a `#file:` reference to
  `.github/copilot-instructions.md`.

### Expected Response Format

- **Be minimal**: default to 1-3 sentences. Expand only when the user explicitly asks
  (e.g., "explain", "elaborate", "detail", "give an example").
- Provide a concise and testable implementation, with PEP 257-compliant docstrings and
  type annotations.
- Add a small `pytest` test when the feature is non-trivial.
- For infrastructure changes, provide the complete manifest (`Dockerfile`, `helm` chart
  snippet) and a brief usage note.
- For commands and instructions, use code blocks with the correct language (bash,
  Dockerfile, yaml).
- Never include secrets or sensitive values in plain text.

## General Preferences

- Code Style: Follow PEP 8, explicit names, short functions (<= 50 lines), type hints
  when possible. Use `ruff format` for formatting and `ruff check` for linting.
- Docstrings: All functions and classes must include a docstring compliant with
  PEP 257; document parameters, return values, and exceptions. Prefer Google or NumPy
  style.
- Testing: Prefer `pytest`; target minimum acceptable coverage (e.g., 80% for critical
  modules).
- Logging: Use the `logging` module with appropriate levels; do not use `print` in
  production.
- Security: Never generate or propose inserting secrets (API keys, passwords). Use
  environment variables and vault solutions.

## Recommended Tools

- Formatting and Linting: `ruff` — replaces `black`, `isort`, and `flake8` in a single
  tool. Configure via `[tool.ruff]` in `pyproject.toml`.
- Git Hooks: use `pre-commit` with `ruff` and `ruff-format` hooks.

## Domain-Specific Guidelines

Rules for FastAPI, auth/security, observability, data engineering, ML training,
inference, MLOps pipelines, EDA, notebooks, and environments are defined in the
path-specific instruction files under `.github/instructions/`. They are applied
automatically based on the active file path (`applyTo` pattern).

## Restrictions and Prohibitions

- Do not generate: secrets, API keys, passwords, or instructions to bypass security.
- Avoid suggestions that hardcode non-reproducible local paths.

## Operational Usage

- This file must remain at the root `.github/copilot-instructions.md` to be recognized.
- To propose a modification: open a small and explicit PR, include tests and validation
  instructions.

## Exclusions and Best Practices

- Do not directly modify CI/CD workflows or secrets; propose PRs and validation
  instructions.
- Avoid non-reproducible local paths and undeclared dependencies.
- Prefer atomic and tested changes; each PR must include tests or a justification.

## PR / Commit Conventions

- Prefer small and targeted PRs with a clear title and description of changes.
- Concise commit messages: `feat:`, `fix:`, `chore:` followed by a brief description.

## Branch Strategy

Branch naming, CI pipeline scope, and merge policies are defined in `./docs/STANDARDS.md`
(present in each target repository). Refer to that file for authoritative branch rules.
