<div align="center">

# Personal Expense Tracking API

A production-ready FastAPI demo showcasing a complete REST API for expense management with authentication, budgeting, and reporting.

**Built with:** FastAPI • SQLAlchemy • Pydantic • SQLite

</div>

![Python](https://img.shields.io/badge/python-3.14-blue.svg) ![FastAPI](https://img.shields.io/badge/framework-FastAPI-green.svg) ![Makefile](https://img.shields.io/badge/Makefile-✓-orange.svg) [![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/) [![GitHub release (latest by date)](https://img.shields.io/github/v/release/Hag-Zilla/DEMO_FastAPI)](https://github.com/Hag-Zilla/DEMO_FastAPI/releases) [![CI](https://github.com/Hag-Zilla/DEMO_FastAPI/actions/workflows/ci-full.yml/badge.svg)](https://github.com/Hag-Zilla/DEMO_FastAPI/actions) [![codecov](https://codecov.io/github/Hag-Zilla/DEMO_FastAPI/graph/badge.svg?branch=develop)](https://app.codecov.io/github/Hag-Zilla/DEMO_FastAPI?branch=develop)

## 📑 Table of Contents

- [📖 About](#about)
- [🎯 Repository Scope](#-repository-scope)
- [🚀 Quick Start](#quick-start)
- [📁 Project Structure](#project-structure)
- [🧩 Service Documentation](#-service-documentation)
- [🛠️ Code Quality & Development Standards](#code-quality--development-standards)
- [📖 Extra documentation](#extra-documentation)
- [📚 Resources](#resources)
- [🤝 Contributing](#contributing)
- [💬 Support](#support)
- [📜 License](#-license)

---

## 📖 About
---

A personal expense tracking API built with **FastAPI** and **SQLite**. Users can manage their expenses, set monthly budgets, receive alerts for budget overruns, and generate detailed expense reports. The project demonstrates best practices in API design, authentication, database modeling, and production-ready application structure.

## 🎯 Repository Scope
---

This root README describes the repository as a whole (workspace layout, shared tooling, entry-point commands, and cross-cutting docs).

Service-level implementation details are intentionally kept out of this file and documented in each service README.

## 🚀 Quick Start
---

```bash
git clone <repo-url>
cd DEMO_FastAPI
make init-env
make init
source .venv/bin/activate
make help
```

For service run/config details, see:

- [services/api/README.md](services/api/README.md)
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)

Common repository-level commands:

```bash
make test
make run-hooks
make clean-hooks
```

For all commands and workflows:

- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md#quick-reference)

## 📁 Project Structure
---

```
DEMO_FastAPI/
│
├── services/                       # Application services workspace
│   ├── api/                        # FastAPI service (code, tests, migrations, logs)
│   └── data/                       # Runtime data such as the SQLite database
│
├── docs/                           # Project-level documentation
├── scripts/                        # Administrative and bootstrap scripts
├── .github/                        # CI workflows and GitHub automation
├── Makefile                        # Common development and maintenance commands
├── pyproject.toml                  # Workspace definition for uv
├── uv.lock                         # Locked dependency set
├── .pre-commit-config.yaml         # Repository quality gates
├── .env.example                    # Environment template
└── README.md                       # Repository overview
```

This section intentionally stays at repository level.
Service-internal layout should be documented in each service's own README rather than expanded in the root README.

**Key Directories:**
- **`services/`** - Contains the runnable services managed by the workspace
- **`docs/`** - Holds cross-cutting documentation for development and standards
- **`scripts/`** - Groups operational and bootstrap scripts
- **`.github/`** - Stores CI/CD workflow definitions

**Root Configuration:**
- **`Makefile`** - Entry point for common local commands
- **`pyproject.toml` + `uv.lock`** - Workspace and dependency lock configuration
- **`.pre-commit-config.yaml`** - Repository-wide code quality automation

## 🧩 Service Documentation
---

Detailed service-level technical documentation is maintained under each service directory.

For the API service, use:

- [services/api/README.md](services/api/README.md)

---

## 🛠️ Code Quality & Development Standards
---

This project maintains strict code quality standards enforced through pre-commit hooks (10+ checks), type hints, Google-style docstrings, and Makefile automation.

**For details:**
- **[docs/STANDARDS.md](docs/STANDARDS.md)** — Code conventions, naming, docstrings, type hints
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** — Development workflow, pre-commit setup, Makefile targets

---

## 📖 Extra documentation

For specialized topics and detailed guides:

| Document | Purpose |
|----------|----------|
| **[services/api/README.md](services/api/README.md)** | API service technical reference (data models, endpoints, auth flow, exceptions) |
| **[docs/RATE_LIMITING.md](docs/RATE_LIMITING.md)** | Rate limiting implementation with slowapi + Redis |
| **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** | Development setup, pre-commit hooks, code quality workflow |
| **[docs/STANDARDS.md](docs/STANDARDS.md)** | Code standards, naming conventions, docstring format, type hints |

## 📚 Resources
---

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Security](https://fastapi.tiangolo.com/advanced/security/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PyJWT Documentation](https://pyjwt.readthedocs.io/)
- [pwdlib Documentation](https://frankie567.github.io/pwdlib/)
- [DBeaver Database Tool](https://dbeaver.io/)

## 🤝 Contributing
---

Contributions are welcome! For detailed guidelines on how to contribute, including:
- Development setup and environment
- Code quality standards and style guides
- Pre-commit hooks and testing requirements
- Commit message guidelines and PR process

Please see [**CONTRIBUTING.md**](CONTRIBUTING.md) for complete instructions.

## 💬 Support
---

> Maintained by [Hag-Zilla](https://github.com/Hag-Zilla)

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0
International License (CC BY-NC 4.0).

See [LICENSE](LICENSE) for the full text.

For commercial use or alternative licensing, contact the maintainers.

---

<div align="center">
  <p>
    <strong>Built with 💪 for reliable expense tracking, clean API design, and smart automation.</strong>
  </p>
  <p>
    ⭐ If this repo helped you, consider starring it!
  </p>
</div>
