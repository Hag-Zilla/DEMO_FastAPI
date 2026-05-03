"""HTTP request/response logging and rate limiting middleware."""

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address

from services.api.core.config import settings
from services.api.core.logging import get_logger

logger = get_logger(__name__)


# Initialize limiter with Redis storage for distributed rate limiting
def get_limiter() -> Limiter:
    """Create and return a configured Limiter instance.

    Uses Redis for distributed quota tracking across multiple instances.
    Falls back to in-memory storage if Redis is unavailable.
    """
    redis_url = settings.REDIS_URL
    if redis_url:
        try:
            redis_limiter = Limiter(
                key_func=get_remote_address,
                storage_uri=redis_url,
                default_limits=["100/minute"],
                swallow_errors=True,
            )
            logger.info("Rate limiter initialized with Redis storage")
            return redis_limiter
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.warning(
                "Failed to initialize Redis limiter, falling back to memory: %s",
                exc,
            )

    return Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        swallow_errors=True,
    )


# Global limiter instance
limiter = get_limiter()


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log HTTP activity."""
        start_time = time.time()

        # Resolve client IP from the direct client connection.
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")

        try:
            response = await call_next(request)
        except Exception:
            duration = time.time() - start_time
            logger.error(
                "%s %s 500 %.3fs %s",
                request.method,
                request.url.path,
                duration,
                client_ip,
                exc_info=True,
                extra={
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "http_status": 500,
                    "duration_ms": round(duration * 1000, 3),
                    "client_ip": client_ip,
                },
            )
            raise

        duration = time.time() - start_time

        log_message = "%s %s %s %.3fs %s"
        log_extra = {
            "http_method": request.method,
            "http_path": request.url.path,
            "http_status": response.status_code,
            "duration_ms": round(duration * 1000, 3),
            "client_ip": client_ip,
            "forwarded_for": forwarded_for,
        }

        logger.info(
            log_message,
            request.method,
            request.url.path,
            response.status_code,
            duration,
            client_ip,
            extra=log_extra,
        )

        return response
