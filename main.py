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
from routes.user_routes import router as user_router
from routes.expense_routes import router as expense_router
from routes.report_routes import router as report_router
from routes.alert_routes import router as alert_router
from routes.admin_routes import router as admin_router
from routes.health_routes import router as health_router
from database import Base, engine

# FastAPI app
app = FastAPI(
    title="Personal Expense Tracking API",
    description="An API to manage personal expenses, set budgets, generate alerts, and create detailed reports.",
    version="1.0.0",
    openapi_tags=[
        {"name": "User Management", "description": "Operations related to user creation and management."},
        {"name": "Expense Management", "description": "Operations to add, update, and delete expenses."},
        {"name": "Budget Management", "description": "Operations to set and update budgets."},
        {"name": "Alerts", "description": "Endpoints to generate alerts for budget overruns."},
        {"name": "Reports", "description": "Endpoints to generate monthly and custom period reports."},
        {"name": "Administrative", "description": "Administrative operations like managing users and accessing reports."}
    ]
)

# Initialize the database
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(user_router, prefix="/users", tags=["User Management"])
app.include_router(expense_router, prefix="/expenses", tags=["Expense Management"])
app.include_router(report_router, prefix="/reports", tags=["Reports"])
app.include_router(alert_router, prefix="/alerts", tags=["Alerts"])
app.include_router(admin_router, prefix="/admin", tags=["Administrative"])
app.include_router(health_router, tags=["Main"])

# ===========================================================================================================================
# =                                                Standalone way                                                        =
# ===========================================================================================================================

if __name__ == '__main__':

    print("Try to do something smart...")
    print("... but I don't know what yet.")
