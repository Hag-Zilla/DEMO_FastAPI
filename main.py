#############################################################################################################################
#                      __  __   ___   _   _  _  __ _____ __   __  _____  ___   ____    ____  _____ 
#                     |  \/  | / _ \ | \ | || |/ /| ____|\ \ / / |  ___|/ _ \ |  _ \  / ___|| ____|
#                     | |\/| || | | ||  \| || ' / |  _|   \ V /  | |_  | | | || |_) || |  _ |  _|  
#                     | |  | || |_| || |\  || . \ | |___   | |   |  _| | |_| ||  _ < | |_| || |___ 
#                     |_|  |_| \___/ |_| \_||_|\_\|_____|  |_|   |_|    \___/ |_| \_\ \____||_____|
#
#############################################################################################################################

"""
    Fast API demo : Expanse tracker API
    Handcraft with love and sweat by : Damien Mascheix @Hagzilla

"""
# ================================================    Modules import     =====================================================

from fastapi import FastAPI
from src.routes.user import router as user_router
from src.routes.expense import router as expense_router
from src.routes.report import router as report_router
from src.routes.alert import router as alert_router
from src.routes.admin import router as admin_router
from src.routes.health import router as health_router
from src.database.database import Base, engine
from src.config import SECRET_KEY


# Enriched tags metadata definition with names, descriptions, routers and prefixes
tags_metadata = [
    {
        "name": "Main",
        "description": "Health check and main operations.",
        "router": health_router,
        "prefix": None
    },
    {
        "name": "User Management",
        "description": "Operations related to user creation and management.",
        "router": user_router,
        "prefix": "/users"
    },
    {
        "name": "Expenses",
        "description": "Operations to add, update, and delete expenses.",
        "router": expense_router,
        "prefix": "/expenses"
    },
    {
        "name": "Reports",
        "description": "Endpoints to generate monthly and custom period reports.",
        "router": report_router,
        "prefix": "/reports"
    },
    {
        "name": "Alerts",
        "description": "Endpoints to generate alerts for budget overruns.",
        "router": alert_router,
        "prefix": "/alerts"
    },
    {
        "name": "Administration",
        "description": "Administrative operations like managing users and accessing reports.",
        "router": admin_router,
        "prefix": "/admin"
    }
]

# FastAPI app
app = FastAPI(
    title="Personal Expense Tracking API",
    description="An API to manage personal expenses, set budgets, generate alerts, and create detailed reports.",
    version="1.0.0",
    openapi_tags=[{"name": tag["name"], "description": tag["description"]} for tag in tags_metadata]
)

# Initialize the database
Base.metadata.create_all(bind=engine)

# Dynamically include routers
for tag in tags_metadata:
    prefix = tag["prefix"] or ""  # Replace None with an empty string
    app.include_router(tag["router"], prefix=prefix, tags=[tag["name"]])


# ===========================================================================================================================
# =                                                Standalone way                                                        =
# ===========================================================================================================================

if __name__ == '__main__':

    print("Try to do something smart...")
    print("... but I don't know what yet.")
