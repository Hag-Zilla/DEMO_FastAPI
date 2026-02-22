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

from fastapi import FastAPI

from .core.config import JWT_EXPIRATION_MINUTES
from .database.session import Base, engine
from .routers import users, auth, health, expenses, alerts, reports

# Initialize the database (create tables)
Base.metadata.create_all(bind=engine)

# Create FastAPI application instance
app = FastAPI(
    title="Personal Expense Tracking API",
    description=(
        "An API to manage personal expenses, set budgets, generate alerts, "
        "and create detailed reports."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "Main", "description": "Health check and main operations."},
        {"name": "Authentication", "description": "Endpoints for user authentication."},
        {"name": "User Management", "description": "Operations related to user creation and management."},
        {"name": "Expenses", "description": "Operations to add, update, and delete expenses."},
        {"name": "Reports", "description": "Endpoints to generate monthly and custom period reports."},
        {"name": "Alerts", "description": "Endpoints to generate alerts for budget overruns."},
    ]
)

# Include all routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(alerts.router)
app.include_router(reports.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Personal Expense Tracking API"}

# ========================================================================
# =                          Standalone way                              =
# ========================================================================

if __name__ == '__main__':

    print("Try to do something smart...")
    print("... but I don't know what yet.")
