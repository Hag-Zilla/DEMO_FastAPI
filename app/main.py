####################################################################################################
#             __  __   ___   _   _  _  __ _____ __   __  _____  ___   ____    ____  _____
#            |  \/  | / _ \ | \ | || |/ /| ____|\ \ / / |  ___|/ _ \ |  _ \  / ___|| ____|
#            | |\/| || | | ||  \| || ' / |  _|   \ V /  | |_  | | | || |_) || |  _ |  _|
#            | |  | || |_| || |\  || . \ | |___   | |   |  _| | |_| ||  _ < | |_| || |___
#            |_|  |_| \___/ |_| \_||_|\_\|_____|  |_|   |_|    \___/ |_| \_\ \____||_____|
#
####################################################################################################

"""
    Fast API demo : Expanse tracker API
    Handcraft with love and sweat by : Damien Mascheix @Hagzilla

"""
# ==================================    Modules import     =========================================

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.exceptions import AppException
from .core.logging import get_logger
from .core.middleware import HTTPLoggingMiddleware
from .database.session import Base, engine
from .routers import users, auth, health, expenses, alerts, reports

# Initialize logger
logger = get_logger(__name__)

# Initialize the database (create tables)
Base.metadata.create_all(bind=engine)

# Create FastAPI application instance
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "An API to manage personal expenses, set budgets, generate alerts, "
        "and create detailed reports."
    ),
    version=settings.APP_VERSION,
    openapi_tags=[
        {"name": "Main", "description": "Health check and main operations."},
        {
            "name": "Authentication",
            "description": "Endpoints for user authentication.",
        },
        {
            "name": "User Management",
            "description": "Operations related to user creation and management.",
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
    ]
)

# Add HTTP logging middleware
app.add_middleware(HTTPLoggingMiddleware)

app.state.startup_complete = False


@app.on_event("startup")
async def on_startup():
    """Mark application startup as completed."""
    app.state.startup_complete = True


@app.on_event("shutdown")
async def on_shutdown():
    """Mark application as not started when shutting down."""
    app.state.startup_complete = False


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):  # pylint: disable=unused-argument
    """Handle custom AppException."""
    logger.warning("AppException: %s (status: %s)", exc.detail, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
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
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(alerts.router)
app.include_router(reports.router)


@app.get("/", name="API Root", tags=["Main"])
async def read_root():
    """Root endpoint."""
    return {"message": "Personal Expense Tracking API"}

# ========================================================================
# =                          Standalone way                              =
# ========================================================================

if __name__ == '__main__':

    print("Try to do something smart...")
    print("... but I don't know what yet.")
