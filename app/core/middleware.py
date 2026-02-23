"""HTTP request/response logging middleware."""

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log HTTP activity."""
        start_time = time.time()

        # Extract client IP (support X-Forwarded-For for proxies)
        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                "%s %s 500 %.3fs %s",
                request.method,
                request.url.path,
                duration,
                client_ip,
            )
            raise

        duration = time.time() - start_time

        # Skip logging for health checks to reduce noise
        if not request.url.path.startswith("/health"):
            logger.info(
                "%s %s %s %.3fs %s",
                request.method,
                request.url.path,
                response.status_code,
                duration,
                client_ip,
            )

        return response
