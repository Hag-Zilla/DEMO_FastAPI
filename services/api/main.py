####################################################################################################
#             __  __   ___   _   _  _  __ _____ __   __  _____  ___   ____    ____  _____
#            |  \/  | / _ \ | \ | || |/ /| ____|\ \ / / |  ___|/ _ \ |  _ \  / ___|| ____|
#            | |\/| || | | ||  \| || ' / |  _|   \ V /  | |_  | | | || |_) || |  _ |  _|
#            | |  | || |_| || |\  || . \ | |___   | |   |  _| | |_| ||  _ < | |_| || |___
#            |_|  |_| \___/ |_| \_||_|\_\|_____|  |_|   |_|    \___/ |_| \_\ \____||_____|
#
####################################################################################################

"""Fast API demo: Expense tracker API.

Handcraft with love and sweat by Damien Mascheix @Hagzilla.
"""
# ==================================    Modules import     =========================================

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from .core.config import settings
from .core.exceptions import AppException
from .core.logging import get_logger
from .core.middleware import HTTPLoggingMiddleware, limiter
from .database.session import Base, engine
from .routers import users, health, expenses, alerts, reports, analytics
from .auth import router as auth_router
from .core.branding import STARTUP_BANNER, LOG_SIGNATURE
from .core.cache import setup_cache

# Initialize logger
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown logic."""
    # --- Startup ---
    Base.metadata.create_all(bind=engine)
    setup_cache(settings.REDIS_URL)
    print(STARTUP_BANNER)
    logger.info(LOG_SIGNATURE)
    logger.info("=" * 70)
    logger.info("🚀 Expense Tracker API is running and ready to accept requests")
    logger.info("=" * 70)
    app.state.startup_complete = True

    yield

    # --- Shutdown ---
    app.state.startup_complete = False


# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "An API to manage personal expenses, set budgets, generate alerts, "
        "and create detailed reports."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Main", "description": "Health check and main operations."},
        {
            "name": "Authentication",
            "description": "Endpoints for user authentication.",
        },
        {
            "name": "User Management",
            "description": "Operations related to user creation, management, and admin approvals.",
        },
        {
            "name": "Expenses",
            "description": "Operations to add, update, and delete expenses.",
        },
        {
            "name": "Reports",
            "description": "Endpoints to generate monthly and custom period reports.",
        },
        {
            "name": "Alerts",
            "description": "Endpoints to generate alerts for budget overruns.",
        },
        {
            "name": "Analytics",
            "description": "Admin-only business analytics and KPI summary.",
        },
    ],
)

# CORS – restrict allow_origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach SlowAPI limiter to app for decorator usage
app.state.limiter = limiter
app.state.startup_complete = False

# Add HTTP logging middleware
app.add_middleware(HTTPLoggingMiddleware)


# Exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors (HTTP 429)."""
    logger.warning(
        "Rate limit exceeded for %s from %s",
        request.url.path,
        request.client.host if request.client else "unknown",
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": exc.detail if hasattr(exc, "detail") else None,
        },
    )


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):  # pylint: disable=unused-argument
    """Handle custom AppException."""
    logger.warning("AppException: %s (status: %s)", exc.detail, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """Log and return request validation errors (HTTP 422)."""
    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):  # pylint: disable=unused-argument
    """Handle general exceptions."""
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include all routers
app.include_router(health.router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")

# Mount static files for assets (must be after all routes!)
static_dir = Path(__file__).parent / "utils" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", name="API Root", tags=["Main"])
def read_root():
    """Root endpoint."""
    return {"message": "Personal Expense Tracking API"}


@app.get("/favicon.svg", include_in_schema=False)
def favicon_svg():
    """Serve the favicon."""
    favicon_path = Path(__file__).parent / "utils" / "static" / "favicon.svg"
    if favicon_path.exists():
        return FileResponse(favicon_path, media_type="image/svg+xml")
    return Response(status_code=204)


@app.get("/favicon.ico", include_in_schema=False)
def favicon_ico():
    """Serve favicon in ICO format (redirect to SVG)."""
    return Response(
        status_code=204,
        headers={"Cache-Control": "public, max-age=31536000"},
    )


@app.get("/metrics", include_in_schema=False)
def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


# ========================================================================
# =                          Standalone way                              =
# ========================================================================

if __name__ == "__main__":
    print("Try to do something smart...")
    print("... but I don't know what yet.")
