"""Initial data bootstrap helpers.

Admin bootstrap is intentionally manual via `make bootstrap-admin` to avoid
storing privileged credentials in environment variables.
"""

from services.api.core.logging import get_logger

logger = get_logger(__name__)


def bootstrap_initial_data() -> None:
    """No-op by design.

    The application no longer creates admin users from environment variables.
    Use the interactive bootstrap script instead.
    """
    logger.debug("Automatic initial data bootstrap is disabled")


def main() -> None:
    """Entry point kept for compatibility with `make init-data`."""
    logger.info(
        "No automatic init-data action. Use 'make bootstrap-admin' for admin creation."
    )


if __name__ == "__main__":
    main()
