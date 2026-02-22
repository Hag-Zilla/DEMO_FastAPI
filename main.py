####################################################################################################
#             __  __   ___   _   _  _  __ _____ __   __  _____  ___   ____    ____  _____
#            |  \/  | / _ \ | \ | || |/ /| ____|\ \ / / |  ___|/ _ \ |  _ \  / ___|| ____|
#            | |\/| || | | ||  \| || ' / |  _|   \ V /  | |_  | | | || |_) || |  _ |  _|
#            | |  | || |_| || |\  || . \ | |___   | |   |  _| | |_| ||  _ < | |_| || |___
#            |_|  |_| \___/ |_| \_||_|\_\|_____|  |_|   |_|    \___/ |_| \_\ \____||_____|
#
####################################################################################################

"""
    Fast API demo : Expense Tracker API
    Handcraft with love and sweat by : Damien Mascheix @Hagzilla

    This entry point exports the FastAPI application instance.
    Use with: uvicorn main:app --reload
"""

from app.main import app

# Alias for alternative uvicorn import
api = app

if __name__ == "__main__":
    """For development. Use uvicorn main:app --reload in production."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
