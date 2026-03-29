# Scripts Directory

This directory contains administrative and setup scripts for the DEMO_FastAPI project.

## Overview

| Script | Purpose | Audience |
|--------|---------|----------|
| `setup.sh` | Environment initialization and dependencies | Developers |
| `project_spec.sh` | Admin account bootstrap & database initialization | Administrators |
| `firewall-rules.sh` | DDoS protection (ufw + nftables rules) | DevOps/Admins |

---

## `setup.sh` - Development Environment Setup

Initializes the development environment with appropriate Python package manager.

### Environment Managers Supported
- `uv` - Ultra-fast Python package installer (recommended)
- `pip` - Standard Python package manager
- `conda` - Conda environment manager
- `pipenv` - Pipenv virtual environment
- Poetry - Poetry dependency manager

### Usage

```bash
# Option 1: Run without arguments - auto-detects manager
./scripts/setup.sh

# Option 2: Specify environment manager explicitly
PYTHON_ENV_MANAGER=uv ./scripts/setup.sh
PYTHON_ENV_MANAGER=pip ./scripts/setup.sh
PYTHON_ENV_MANAGER=conda ./scripts/setup.sh
```

### What It Does
1. Detects installed Python environment manager
2. Creates virtual environment
3. Installs dependencies from `requirements.txt` or `pyproject.toml`
4. Triggers admin bootstrap script
5. Displays startup banner

### Requirements
- Python 3.10+
- One of: uv, pip, conda, pipenv, or poetry

---

## `project_spec.sh` - Admin & Database Initialization

Bootstraps the application with initial admin account and database setup.

### Usage

```bash
# Make script executable
chmod +x ./scripts/project_spec.sh

# Run it
./scripts/project_spec.sh
```

### Prompts
- Admin username (e.g., "admin")
- Admin password (with strength validation)
- Admin password confirmation
- Monthly budget for admin account (default recommendations shown)

### What It Does
1. Validates Python installation
2. Initializes SQLite database with ORM models
3. Creates admin user account with ACTIVE status (bypass pending approval)
4. Sets admin role and budget
5. Logs bootstrap completion

### Database
- Default location: `app.db` (SQLite in project root)
- Schema: Defined in `app/database/models/`
  - User table (username, role, status, budget)
  - Expense table (amount, category, date, user_id)

---

## `firewall-rules.sh` - DDoS Protection

Configures firewall rules to protect against DDoS attacks and secure API access.

### Usage

```bash
# Make script executable
chmod +x ./scripts/firewall-rules.sh

# Run as root/sudo (required for ufw and nftables)
sudo ./scripts/firewall-rules.sh
```

### Features

#### UFW Rules
- **Block**: Direct access to FastAPI (`8000`) and Redis (`6379`)
- **Allow**: HTTP (`80`) and HTTPS (`443`) through Nginx reverse proxy
- **Rate limiting**: Basic DDoS mitigation at firewall level

#### nftables Rules
- Implements stateful packet inspection
- Rate limits connections per source IP
- Protects against SYN floods
- Blocks invalid packet states

### Protected Ports
- `8000`: FastAPI (blocked - use Nginx on 80/443)
- `6379`: Redis (blocked - internal network only)
- `5432`: PostgreSQL (blocked - internal network only)
- `80,443`: HTTP/HTTPS (allowed through Nginx)

### Assumptions
- System uses `ufw` (Ubuntu/Debian) or `nftables` (other Linux distributions)
- Nginx is reverse proxy running on ports 80/443
- Internal services are not directly exposed

---

## Running All Setup Scripts

To fully initialize a fresh environment:

```bash
# 1. Setup development environment
./scripts/setup.sh

# 2. Bootstrap database & admin account
./scripts/project_spec.sh

# 3. Configure firewall (requires sudo)
sudo ./scripts/firewall-rules.sh

# 4. Start the application
uvicorn app.main:app --reload
```

---

## Makefile Integration

All scripts are referenced in the `Makefile` for convenience:

```bash
# Development setup
make setup

# Admin bootstrap
make init-db

# Firewall configuration
make setup-firewall
```

See [Makefile](../Makefile) for additional commands.

---

## Troubleshooting

### Setup Script Fails
- Ensure Python 3.10+ is installed: `python --version`
- Check that one of the supported package managers is installed
- If using custom environment manager, set `PYTHON_ENV_MANAGER` variable

### Admin Bootstrap Fails
- Database may already exist - delete `app.db` to reinitialize
- Check file permissions - ensure write access to project directory
- Verify Python dependencies are installed: `pip list | grep fastapi`

### Firewall Script Fails
- Requires `sudo` - run with elevation
- If using `nftables`, ensure kernel `netfilter` support is enabled
- Check systemd status: `systemctl status ufw` or `systemctl status nftables`

---

## Contributing

When adding new scripts:
1. Place in `scripts/` directory
2. Add documentation to this README
3. Update Makefile targets if appropriate
4. Ensure scripts are executable: `chmod +x script.sh`
5. Add error handling and logging
6. Include usage examples

---

## Related Documentation

- [DEVELOPMENT.md](../doc/DEVELOPMENT.md) - Development workflow and Makefile
- [DEPLOYMENT.md](../doc/DEPLOYMENT.md) - Production deployment guide
- [STANDARDS.md](../doc/STANDARDS.md) - Code standards and project conventions
