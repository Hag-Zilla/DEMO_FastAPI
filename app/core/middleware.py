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
        client_ip = (
            request.headers.get("X-Forwarded-For")
            or (request.client.host if request.client else "unknown")
        )

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
