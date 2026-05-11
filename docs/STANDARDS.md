# Development Standards

This document is the **MyBro Governance Contract** shared across repositories.
It defines mandatory principles, decision rules, and policy boundaries.

This file is intentionally generic and conceptual. Detailed implementation rules,
path-specific conventions, and coding patterns must live in:

- `.github/instructions/*.instructions.md`

---

## Table of Contents

1. [Purpose and Positioning](#purpose-and-positioning)
2. [Normative Hierarchy and Conflict Resolution](#normative-hierarchy-and-conflict-resolution)
3. [Applicability Profiles](#applicability-profiles)
4. [Technology Decision Policy](#technology-decision-policy)
5. [Architecture Baseline (Max Target Model)](#architecture-baseline-max-target-model)
6. [Target Directory Structure](#target-directory-structure)
7. [Code Style Policy](#code-style-policy)
8. [Testing Policy](#testing-policy)
9. [Security Policy](#security-policy)
10. [Data Engineering Policy](#data-engineering-policy)
11. [API Design Policy](#api-design-policy)
12. [Observability Policy](#observability-policy)
13. [Branch and Release Strategy](#branch-and-release-strategy)
14. [Decision Records and Deviations](#decision-records-and-deviations)

---

## Purpose and Positioning

- This file defines **repository governance standards** that are stable across projects.
- It does not store low-level examples, snippets, or implementation recipes.
- Service-level documentation belongs in each service README.
- Root README must remain repository-level and must not duplicate service internals.

---

## Normative Hierarchy and Conflict Resolution

Use this order of precedence:

1. Platform/system policies
2. Direct user request (current conversation)
3. `docs/STANDARDS.md` (this file)
4. `.github/instructions/*.instructions.md` (contextual implementation rules)
5. Service-level README files

Conflict resolution rules:

- Prefer the more specific rule when scope differs.
- If equally specific, prefer the most recent explicit decision in this file.
- Any unresolved conflict must be documented as a deviation in this file.

---

## Applicability Profiles

Policies in this file use explicit applicability markers:

- **Always**: applies to all repositories.
- **If API**: applies when the repository exposes HTTP APIs.
- **If Data Pipeline**: applies when the repository runs ETL/ELT pipelines.
- **If Deployed Service**: applies when software is deployed and operated in runtime environments.

Rules remain strict inside their applicability scope.

---

## Technology Decision Policy

Every repository must declare a primary stack profile and supporting tools.

### Strong default profile (Python service full-feature)

| Concern | Default Decision |
| --- | --- |
| Language | Python >= 3.11 |
| API framework (If API) | FastAPI |
| Data validation | Pydantic v2 |
| ORM + migrations | SQLAlchemy + Alembic |
| Formatter / Linter | ruff |
| Test runner | pytest |
| Dependency management | uv |
| Git hooks | pre-commit |

Additional capabilities (If Data Pipeline / If ML) may include dedicated tooling
(for example Pandera, MLflow, DVC) and must be explicitly declared per repo.

Deviations from the selected profile require a documented decision in this file.

---

## Architecture Baseline (Max Target Model)

The default architecture is the **max target model** (full feature set):

| Layer | Responsibility |
| --- | --- |
| API | Contract surface, transport validation, auth entry controls |
| Application | Use-case orchestration and transaction boundaries |
| Domain | Core business rules and invariants |
| Data | Persistence, repositories, migrations |
| Platform | Config, logging, metrics, tracing, runtime integrations |

Mandatory architecture invariants:

- Dependency direction is inward only.
- Domain logic must remain framework-agnostic.
- External integrations are isolated behind adapters.
- Cross-cutting concerns are centralized and reusable.

**Controlled simplification rule**:

- Repositories may prune layers when requirements do not justify full complexity.
- Pruning is allowed only if boundaries stay explicit and no hidden coupling is introduced.
- Every simplification must be recorded in [Decision Records and Deviations](#decision-records-and-deviations).

---

## Target Directory Structure

Repository structure is a mandatory project-level decision.

Hard requirements:

- Separate source code, tests, docs, scripts, and assets at top level.
- Keep business logic isolated from framework and infrastructure concerns.
- Use predictable naming and stable package boundaries.
- Keep service-level technical documentation in service-local README files.

Detailed layout and path rules are defined in:

- `.github/instructions/project-structure.instructions.md`

---

## Code Style Policy

Applicability: **Always**

- Enforce formatter/linter output (no manual overrides).
- Maximum function length: 50 lines (extract helpers when exceeded).
- Public classes/functions must have docstrings following repository conventions.
- Type hints are mandatory on function signatures when language/tooling supports it.
- No magic numbers inline: use named constants.
- No `print` in production code: use structured logging.

---

## Testing Policy

Applicability: **Always**

- Minimum coverage target: 80% on critical modules.
- Unit tests must be isolated from I/O, network, and external services.
- Integration tests requiring external services must be separated by test scope.
- Every new public behavior must include at least one success-path and one error-path test.
- Test names follow the `test_<unit>_<scenario>` convention.

---

## Security Policy

Applicability: **Always** (with API-specific constraints under *If API*)

- Secrets must never be hardcoded.
- `.env` is git-ignored; `.env.example` contains placeholders only.
- Access control and authentication failures must return explicit, consistent status codes.
- SQL execution must be parameterized; string interpolation in SQL is prohibited.

If API:

- Authn/Authz mechanisms must be centralized and reusable.
- Token/session lifecycles must be explicitly defined and documented.
- Production CORS and exposure settings must be least-privilege.

---

## Data Engineering Policy

Applicability: **If Data Pipeline**

- Pipelines must be idempotent.
- Prefer incremental processing over full reloads when possible.
- Failed records must be captured; silent discard is prohibited.
- Input/output row counts must be logged per pipeline step.
- Schema changes must use migration tooling; manual drift is prohibited.
- Migrations must be reversible unless explicitly justified.

---

## API Design Policy

Applicability: **If API**

- Route modules are organized by domain (no monolithic router files).
- Endpoints must declare explicit response semantics and status codes.
- Exception mapping is centralized (not ad-hoc per route).
- Contracts (schemas/errors/versioning) must be stable and documented.

---

## Observability Policy

Applicability: **If Deployed Service**

- Logs must be structured and machine-consumable.
- Metrics must be defined consistently and avoid high-cardinality labels.
- Metrics and traces must support incident diagnosis and SLO tracking.
- Operational endpoints and dashboards must be documented.

---

## Branch and Release Strategy

| Branch | Purpose |
| --- | --- |
| `main` | Production-stable. Protected. Merge via PR only. |
| `develop` | Integration branch. All feature branches merge here first. |
| `feature/<ticket>-<description>` | One branch per feature or fix. |

- All PRs must have CI green before merge.
- Commit messages require a typed prefix: `feat:`, `fix:`, `chore:`, `docs:`.
- Releases are tagged on `main` with semver (`v1.2.3`).

---

## Decision Records and Deviations

Any significant deviation from this standard must be recorded with:

1. Date
2. Decision summary
3. Rationale
4. Scope (which repos/modules are affected)
5. Expiration or review date (if temporary)

If a repository uses ADRs, reference the ADR identifier here.

---

Last updated: 2026-05-11
