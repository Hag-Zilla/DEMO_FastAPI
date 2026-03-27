"""HTTP request/response logging and rate limiting middleware."""

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_client import Counter, Histogram, Gauge

from app.core.logging import get_logger

logger = get_logger(__name__)

# ==================== Prometheus Metrics ====================
# HTTP Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# Rate limiting metrics
rate_limit_hits_total = Counter(
    "rate_limit_hits_total",
    "Total rate limit rejections",
    ["zone", "client_ip"],
)

# Redis connectivity metrics
redis_connection_errors_total = Counter(
    "redis_connection_errors_total",
    "Total Redis connection errors",
)
redis_connected = Gauge(
    "redis_connected",
    "Redis connection status (1=connected, 0=disconnected)",
)


# Initialize limiter with Redis storage for distributed rate limiting
def get_limiter() -> Limiter:
    """Create and return a configured Limiter instance.

    Uses Redis for distributed quota tracking across multiple instances.
    Falls back to in-memory storage if Redis is unavailable.
    """
    try:
        import os

        redis_url = os.getenv(
            "REDIS_URL", "redis://:redis_secure_password@redis:6379/0"
        )
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=redis_url,
            default_limits=["100/minute"],  # Default: 100 req/min per IP
            swallow_errors=True,  # Don't break app if Redis fails
        )
        logger.info("Rate limiter initialized with Redis storage")
        return limiter
    except Exception as e:
        logger.warning(
            "Failed to initialize Redis limiter, falling back to memory: %s", e
        )
        limiter = Limiter(
            key_func=get_remote_address,
            default_limits=["100/minute"],
            swallow_errors=True,
        )
        return limiter


# Global limiter instance
limiter = get_limiter()


class HTTPLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log HTTP activity."""
        start_time = time.time()

        # Extract client IP (support X-Forwarded-For for proxies)
        client_ip = request.headers.get("X-Forwarded-For") or (
            request.client.host if request.client else "unknown"
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

        # Record Prometheus metrics
        endpoint = request.url.path
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code,
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(duration)

        return response
