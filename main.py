#############################################################################################################################
#                                                            main                                                           #
#############################################################################################################################

# ================================================          Header           ================================================

"""

Title : main.py
Init craft date : 03/10/2022
Handcraft with love and sweat by : Damien Mascheix @Hagzilla
Notes :
    Main script for the FastAPI exam

"""
# ================================================       Optimisations        ================================================

""" 
shh, an idea grows

"""

# ================================================    Modules import     =====================================================

# Classics
import pandas as pd
import os

# Fast API
from fastapi import FastAPI

# # URL management
# from urllib.parse import urlparse

# # MLFLOW
# import mlflow

# # Modeling
# from sklearn import svm, datasets 
# from sklearn.model_selection import GridSearchCV 

# # Script timing
# import time
# start_time = time.time()

# ================================================          Functions          ================================================

""" Nothing there """

# ================================================          Warfield          ================================================

# ===================== API instace
api = FastAPI(title="My first API \m/",
              description="My first API powered by FastAPI.",
              version="1.0.0",
              openapi_tags=[{'name': 'Main','description': 'main functions'},
                            {'name': 'Questions management','description': 'Questions management'}
                            ]
              )


# ===================== Common responses customization
responses = {200: {"description": "OK"},
             404: {"description": "Item not found"},
             302: {"description": "The item was moved"},
             403: {"description": "Not enough privileges"},
             }

# ===================== Requests management

# Health request
@api.get('/health',responses=responses, name="Health check of the API",tags=['Main'])
def get_health():
    """_summary_
    \n
    Request to check the API's health
    \n
    Returns:
        JSON : Current state of the APP
    """

    return {'state': 'API is currently running. Please proceed'
            }




# ===========================================================================================================================
# =                                                Debug WORLD !!!!!                                                        =
# ===========================================================================================================================

if __name__ == '__main__':

    # Identifying the parent directory of the script
    curr_script_dir = os.path.dirname(__file__)

    # Read the "database"
    database = pd.read_csv(filepath_or_buffer = curr_script_dir+"/DB/questions.csv")

    # # Debug only
    # print(df.head())

    # users = {"alice": "wonderland",
    #         "bob": "builder",
    #         "clementine": "mandarine"}

    # @api.get("/")
    # async def root():
    #     return {"message": "Hello World"}

