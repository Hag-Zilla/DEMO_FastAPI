---
applyTo: "apps/**,domains/**,infra/**,transverse/**,tools/**,docs/**,security/**,supply-chain/**,services/**,tests/**,scripts/**,notebooks/**"
---

## Purpose

Enforce a consistent project layout across all repositories so Copilot generates files,
imports, and references that match the expected directory structure.

## Expected Directory Layout

Use this exact baseline monorepo structure unless an ADR explicitly approves a deviation.

<!-- cspell:disable -->
```text
my-project/                                        # Racine du monorepo
├─ README.md                                       # Vue d'ensemble du projet
├─ CONTRIBUTING.md                                 # Regles de contribution
├─ AGENTS.md                                       # Referentiel global de l'agentique et de son usage
├─ LICENSE                                         # Licence
│
├─ .gitignore                                      # Exclusions Git
├─ .editorconfig                                   # Regles d'edition communes
├─ .python-version                                 # Version Python de reference
├─ .env.example                                    # Variables d'environnement generiques d'exemple
├─ .env.docker.dev.example                         # Variables d'environnement pour le dev Docker
├─ .pre-commit-config.yaml                         # Hooks pre-commit
├─ .secrets.baseline                               # Baseline detect-secrets
├─ mypy.ini                                        # Configuration mypy
├─ pytest.ini                                      # Configuration pytest
│
├─ pyproject.toml                                  # Configuration Python racine pour l'environnement global du repo
├─ uv.lock                                         # Lockfile uv versionne
├─ Makefile                                        # Commandes standardisees
├─ compose.yaml                                    # Orchestration locale multi-conteneurs
│
├─ .github/
│  └─ workflows/
│     ├─ ci-light.yml                              # CI legere
│     └─ ci-full.yml                               # CI complete incluant securite, SBOM et validations etendues
│
├─ docs/
│  ├─ STANDARDS.md                                 # Standards globaux du projet
│  ├─ architecture/                                # Vues d'architecture et principes de structuration
│  ├─ adr/                                         # Architecture Decision Records
│  ├─ runbooks/                                    # Runbooks globaux transverses
│  ├─ service-catalog/                             # Catalogue global des services : owner, criticite, dependances
│  ├─ reliability/                                 # SLI/SLO, budgets d'erreur, conventions de fiabilite
│  ├─ continuity/                                  # BIA, RTO/RPO, DR, backup/restore
│  ├─ diagrams/                                    # Diagrammes
│  └─ conventions/                                 # Conventions detaillees
│
├─ security/                                       # Securite applicative et gouvernance
│  ├─ asvs/                                        # Baseline OWASP ASVS et mapping des controles
│  ├─ threat-models/                               # Modeles de menace
│  ├─ exceptions/                                  # Derogations securite documentees
│  └─ incident-response/                           # Procedures et modeles de reponse a incident
│
├─ supply-chain/                                   # Securite de la chaine logicielle
│  ├─ sbom/                                        # Politiques et artefacts SBOM
│  ├─ provenance/                                  # Provenance / attestations d'artefacts
│  ├─ slsa/                                        # Niveau cible et controles SLSA
│  └─ policies/                                    # Regles de signature, provenance, validation des artefacts
│
├─ apps/                                           # Points d'entree principaux du systeme
│  ├─ ui/                                          # Frontend
│  │  ├─ README.md                                 # Documentation locale du frontend
│  │  ├─ service.yaml                              # Metadonnees du service : owner, criticite, dependances, exposition
│  │  ├─ runbooks/                                 # Runbooks locaux du service
│  │  ├─ src/                                      # Code source UI
│  │  ├─ public/                                   # Assets statiques
│  │  ├─ tests/
│  │  │  ├─ unit/
│  │  │  ├─ integration/
│  │  │  ├─ contract/
│  │  │  └─ security/
│  │  └─ Dockerfile                                # Image du frontend
│  │
│  ├─ api/                                         # API gateway fonctionnelle exposee a l'exterieur
│  │  ├─ README.md                                 # Documentation locale du backend
│  │  ├─ service.yaml                              # Metadonnees du service
│  │  ├─ runbooks/                                 # Runbooks locaux du service
│  │  ├─ Dockerfile                                # Image du backend
│  │  ├─ alembic.ini                               # Configuration Alembic si migrations cote backend
│  │  ├─ pyproject.toml                            # Configuration Python locale du backend si souhaitee
│  │  ├─ app/
│  │  │  ├─ api/                                   # Routes et endpoints FastAPI externes
│  │  │  ├─ core/                                  # Config centrale, securite, bootstrap
│  │  │  ├─ models.py                              # Modeles backend selon le template
│  │  │  ├─ crud.py                                # CRUD selon le template
│  │  │  ├─ main.py                                # Point d'entree FastAPI
│  │  │  ├─ services/                              # Orchestration et composition des services metier internes
│  │  │  ├─ repositories/                          # Adaptateurs vers ressources externes
│  │  │  └─ schemas/                               # Schemas exposes localement par l'API gateway
│  │  ├─ scripts/                                  # Scripts backend
│  │  ├─ contracts/
│  │  │  ├─ openapi/                               # Contrat HTTP externe du service
│  │  │  ├─ schemas/                               # Schemas de payload
│  │  │  └─ errors/                                # Erreurs exposees
│  │  └─ tests/
│  │     ├─ unit/
│  │     ├─ integration/
│  │     ├─ contract/
│  │     ├─ security/
│  │     └─ performance/
│  │
│  └─ notebooks/                                   # Espace notebooks traite comme app de travail
│     ├─ README.md                                 # Documentation locale des notebooks
│     ├─ service.yaml                              # Metadonnees de l'espace notebooks
│     ├─ exploratory/
│     ├─ validation/
│     ├─ reporting/
│     ├─ _templates/
│     ├─ samples/
│     ├─ runbooks/
│     ├─ tests/
│     └─ Dockerfile
│
├─ domains/                                        # Services metier autonomes exposant des APIs internes
│  ├─ service1/
│  │  ├─ README.md                                 # Role, perimetre, dependances et exposition du service
│  │  ├─ service.yaml                              # Owner, criticite, dependances, SLO, endpoints internes
│  │  ├─ runbooks/                                 # Procedures d'exploitation du service
│  │  ├─ Dockerfile                                # Image du service
│  │  ├─ pyproject.toml                            # Optionnel : config locale si service Python
│  │  ├─ src/
│  │  │  ├─ api/                                   # API interne du service
│  │  │  ├─ core/                                  # Config locale, bootstrap, securite interne
│  │  │  ├─ models/
│  │  │  ├─ services/
│  │  │  ├─ repositories/
│  │  │  ├─ schemas/
│  │  │  └─ main.py
│  │  ├─ contracts/
│  │  │  ├─ openapi/
│  │  │  ├─ schemas/
│  │  │  └─ errors/
│  │  └─ tests/
│  │     ├─ unit/
│  │     ├─ integration/
│  │     ├─ contract/
│  │     ├─ security/
│  │     └─ performance/
│  │
│  ├─ service2/
│  │  ├─ README.md
│  │  ├─ service.yaml
│  │  ├─ runbooks/
│  │  ├─ Dockerfile
│  │  ├─ pyproject.toml
│  │  ├─ src/
│  │  ├─ contracts/
│  │  └─ tests/
│  │
│  ├─ service3/
│  │  ├─ README.md
│  │  ├─ service.yaml
│  │  ├─ runbooks/
│  │  ├─ Dockerfile
│  │  ├─ pyproject.toml
│  │  ├─ src/
│  │  ├─ contracts/
│  │  └─ tests/
│  │
│  └─ shared/                                      # Socle metier minimal reellement commun
│     ├─ README.md
│     ├─ src/
│     └─ tests/
│
├─ infra/                                          # Infrastructure, exploitation et services de fondation
│  ├─ dev/
│  │  ├─ compose/
│  │  ├─ seed/
│  │  └─ scripts/
│  │
│  ├─ identity/
│  │  ├─ README.md
│  │  ├─ service.yaml                              # Metadonnees du service transverse
│  │  ├─ runbooks/
│  │  ├─ config/
│  │  ├─ contracts/
│  │  └─ tests/
│  │
│  ├─ database/
│  │  ├─ postgres/
│  │  ├─ backups/
│  │  ├─ migrations/
│  │  ├─ runbooks/
│  │  └─ tests/
│  │
│  ├─ storage/
│  │  ├─ s3/
│  │  ├─ blob/
│  │  ├─ lifecycle/
│  │  └─ tests/
│  │
│  ├─ search/
│  │  ├─ README.md
│  │  ├─ vector-db/
│  │  ├─ backups/
│  │  ├─ runbooks/
│  │  └─ tests/
│  │
│  ├─ k8s/
│  │  ├─ base/
│  │  ├─ overlays/
│  │  ├─ helm/
│  │  └─ tests/
│  │
│  ├─ terraform/
│  │  ├─ modules/
│  │  ├─ environments/
│  │  └─ tests/
│  │
│  └─ containers/
│     ├─ base-python/
│     ├─ base-node/
│     └─ shared/
│
├─ transverse/                                     # Capacites techniques partagees par plusieurs services
│  ├─ observability/
│  │  ├─ opentelemetry/
│  │  ├─ prometheus/
│  │  ├─ loki/
│  │  ├─ grafana/
│  │  ├─ alerts/
│  │  ├─ slos/                                     # SLI/SLO et budgets d'erreur
│  │  ├─ dashboards/                               # Dashboards de reference
│  │  ├─ playbooks/                                # Playbooks d'incident et de diagnostic
│  │  └─ tests/
│  │
│  ├─ airflow/
│  │  ├─ README.md
│  │  ├─ dags/
│  │  ├─ plugins/
│  │  ├─ include/
│  │  ├─ contracts/
│  │  └─ tests/
│  │
│  ├─ nats/
│  │  ├─ README.md
│  │  ├─ streams/
│  │  ├─ consumers/
│  │  ├─ subjects.md
│  │  ├─ contracts/
│  │  │  ├─ events/
│  │  │  └─ schemas/
│  │  └─ tests/
│  │
│  ├─ retrieval/
│  │  ├─ README.md
│  │  ├─ indexer/
│  │  ├─ pipelines/
│  │  ├─ indexes/
│  │  ├─ stores/
│  │  ├─ fusion/
│  │  ├─ evals/
│  │  ├─ contracts/
│  │  └─ tests/
│  │
│  └─ agentic/
│     ├─ README.md
│     ├─ runtime/
│     ├─ workers/
│     ├─ tools/
│     ├─ memory/
│     ├─ evals/
│     ├─ safety/
│     ├─ config/
│     │  ├─ agents/
│     │  ├─ policies/
│     │  ├─ workflows/
│     │  ├─ decisions/
│     │  └─ profiles/
│     ├─ contracts/
│     │  ├─ tools/
│     │  ├─ schemas/
│     │  └─ guardrails/
│     └─ tests/
│
└─ tools/
   ├─ scripts/
   ├─ generators/
   └─ devcli/
```
<!-- cspell:enable -->

Service-level source roots may differ (`app/`, `src/`, or language-specific layouts),
but each service must keep the same internal boundaries.

## Guidelines

- Treat the repository as a monorepo with explicit bounded contexts: `apps/`,
  `domains/`, `infra/`, and `transverse/`.
- Every executable service folder must include `README.md`, `service.yaml`,
  `runbooks/`, `contracts/`, and `tests/`.
- Never place production modules at repository root.
- Test suites must be split by intent: `unit`, `integration`, `contract`, `security`,
  and `performance` (if relevant).
- Keep external contracts versioned and colocated under each service `contracts/`.
- `docs/adr/` is required for architecture decisions with impact across services.
- `notebooks/` under `apps/notebooks/` is a managed workspace, not a dumping folder.
- `scripts/` and `tools/` must be deterministic and automation-friendly.
- Use snake_case for all Python file and directory names.
- Each Python package directory must contain an `__init__.py`.
- New top-level directories require a justification comment in `README.md`.

### Naming Conventions

- **Functions and variables**: `snake_case` — `process_payment()`, `user_count`
- **Classes**: `PascalCase` — `UserService`, `HTTPClient`
- **Constants**: `SCREAMING_SNAKE_CASE` — `MAX_RETRIES`, `DEFAULT_TIMEOUT`
- **Private items**: `_underscore_prefix` — `_internal_helper()`, `_config_cache`
- Never use double underscore (`__`) except for Python name mangling
- Never use camelCase for Python identifiers

### Python File Internal Structure

Every Python module must follow this section order:

1. File docstring
2. Imports (stdlib → third-party → local, alphabetical within each group)
3. Constants (`SCREAMING_SNAKE_CASE`; private constants with `_prefix`)
4. Private helpers (functions and classes prefixed with `_`)
5. Public classes and functions
6. Module setup and exports (`__all__`, router registration)
7. CLI entry point (`if __name__ == "__main__":`) when applicable

## Examples

```text
# Correct: gateway API implementation
apps/api/app/api/v1/users.py

# Correct: domain service and matching tests
domains/service1/src/services/billing.py
domains/service1/tests/unit/test_billing.py

# Correct: shared transverse capability
transverse/observability/prometheus/rules.yaml

# Wrong: module at repo root
myapp_utils.py
```
