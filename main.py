####################################################################################################
#             __  __   ___   _   _  _  __ _____ __   __  _____  ___   ____    ____  _____
#            |  \/  | / _ \ | \ | || |/ /| ____|\ \ / / |  ___|/ _ \ |  _ \  / ___|| ____|
#            | |\/| || | | ||  \| || ' / |  _|   \ V /  | |_  | | | || |_) || |  _ |  _|
#            | |  | || |_| || |\  || . \ | |___   | |   |  _| | |_| ||  _ < | |_| || |___
#            |_|  |_| \___/ |_| \_||_|\_\|_____|  |_|   |_|    \___/ |_| \_\ \____||_____|
#
####################################################################################################

"""
    Fast API demo : Expense tracker API
    Handcraft with love and sweat by : Damien Mascheix @Hagzilla

"""
# ==================================    Modules import     =========================================

from fastapi import FastAPI

from app.api.v1.endpoints import users, auth, health, expenses, reports, alerts
from app.db.session import Base, engine


# Enriched tags metadata definition with names, descriptions, routers and prefixes
tags_metadata = [
    {
        "name": "Main",
        "description": "Health check and main operations.",
        "router": health.router,
        "prefix": None
    },
    {
        "name": "Authentication",
        "description": "Endpoints for user authentication.",
        "router": auth.router,
        "prefix": "/token"
    },
    {
        "name": "User Management",
        "description": "Operations related to user creation and management.",
        "router": users.router,
        "prefix": "/users"
    },
    {
        "name": "Expenses",
        "description": "Operations to add, update, and delete expenses.",
        "router": expenses.router,
        "prefix": "/expenses"
    },
    {
        "name": "Reports",
        "description": "Endpoints to generate monthly and custom period reports.",
        "router": reports.router,
        "prefix": "/reports"
    },
    {
        "name": "Alerts",
        "description": "Endpoints to generate alerts for budget overruns.",
        "router": alerts.router,
        "prefix": "/alerts"
    }
]

# FastAPI app
app = FastAPI(
    title="Personal Expense Tracking API",
    description=(
        "An API to manage personal expenses, set budgets, generate alerts, "
        "and create detailed reports."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": tag["name"], "description": tag["description"]}
        for tag in tags_metadata
    ]
)

# Initialize the database
Base.metadata.create_all(bind=engine)

# Dynamically include routers
for tag in tags_metadata:
    prefix = tag["prefix"] if tag["prefix"] is not None else ""
    app.include_router(
        tag["router"],
        prefix=prefix,
        tags=[tag["name"]],
    )


# ========================================================================
# =                          Standalone way                              =
# ========================================================================

if __name__ == '__main__':

    print("Try to do something smart...")
    print("... but I don't know what yet.")


# Alias for uvicorn compatibility
api = app
