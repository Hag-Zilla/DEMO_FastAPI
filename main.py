#############################################################################################################################
#                                                            main                                                           #
#############################################################################################################################

# ================================================          Header           ================================================

"""

Title : main.py
Init craft date : 03/10/2022
Handcraft with love and sweat by : Damien Mascheix @Hagzilla
Notes :
    Main script for the Fastapi exam

"""
# ================================================       Optimisations        ================================================

""" 
shh, an idea grows

"""

# ================================================    Modules import     =====================================================

# Classics
import pandas as pd
import os
import json

# Fast api
from fastapi import FastAPI
from fastapi import Header, Body
from pydantic import Required
from pydantic import BaseModel
from typing import Optional

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

# ==================== API instace
api = FastAPI(title="My first API \m/",
              description="My first API powered by Fastapi.",
              version="1.0.0",
              openapp_tags=[{'name': 'main','description': 'main functions'},
                            {'name': 'Administration','description': 'Questions management'},
                            {'name': 'Testing area','description': 'Testing area'}
                            ]
              )



# ===================== Common responses customization
responses = {200: {"description": "OK"},
             404: {"description": "Item not found"},
             302: {"description": "The item was moved"},
             403: {"description": "Not enough privileges"},
             }

# ===================== Load users database

with open('./DB/users.json', 'r') as f:
    users = json.load(f)

# Debug (to delete)
print(users)

# ===================== Load questions database

db_quest = pd.read_csv(filepath_or_buffer = "./DB/questions.csv")


# ===================== Requests management

# Health request
@api.get('/health', name="Health check of the API",tags=['main'],responses=responses)
def get_health():
    """_summary_
    \n
    Request to check the API's health
    \n
    Returns:
        JSON : Current state of the API
    """

    return {'state': 'API is currently running. Please proceed'}

#  ========================================================================================================================

class quest_struct(BaseModel):
    """
    Define the structure of a question
    """
    question: str
    subject: str
    use: str
    correct: str
    responseA: str
    responseB: str
    responseD: Optional[str] = None 
    responseD: Optional[str] = None 
    remark : Optional[str] = None 

# Admin / Add questions to the base
@api.post('/admin/new_quest', name='Add question to the base',tags=['Administration'],responses=responses)
def post_content(added_data: quest_struct = Body(None)):
    
    # Debug (to delete)
    print(type(added_data))
    print(added_data)
    print(added_data.dict())  
       
    
    # [value1, value2, value3, ...]
    
    # df.loc[len(df.index)] = [value1, value2, value3, ...]
    
    return {"Following data have been added to the base :" : added_data}






# @app.get('/data', name='Get data', tags=['items'])
# def get_data(index):
#     """returns data
#     """
#     try:
#         return {
#             'data': data[int(index)]
#         }
#     except IndexError:
#         raise HTTPException(
#             status_code=404,
#             detail='Unknown Index')



# class user(BaseModel):
#     """
#     Define the structure of a user's informations
#     """
#     name: str
#     pwd: str

# @app.put('/identification', name='Create a new computer', tags=['Default'])
# def put_computer(user: user = Body()):
#     """Creates a new computer within the database
#     """
#     user.name
#     return {"good"}


# # Admin ID
# @app.get('/admin',responses=responses, name="Admin endpoint",tags=['quest_mgt'])
# def get_health():
#     """_summary_
#     \n
#     Do somme blabla test
#     \n
#     Returns:
#         JSON : blabla test
#     """

#     return users

# from fastapi import Header
# @app.get('/header', name='Get custom header',tags=['items'])
# def get_content(custom_header: Optional[str] = Header(None, description='My own personal header')):
#     """returns a custom header
#     """
#     return {
#         'Custom-Header': custom_header
#     }
   
    

# @app.put('/identification', name='Create a new computer', tags=['items'])
# def put_computer(identification: identification):
#     """Creates a new computer within the database
#     """
#     return identification




#  ========================================================================================================================


# Test requests
@api.get('/test/read_users', name="Debug endpoint",tags=['Testing area'],responses=responses)
def get_users():
    return users

@api.post('/test/wright_users', name="Debug endpoint",tags=['Testing area'],responses=responses)
def post_add_users(username:str,pwd:str):

    if username not in users.keys():
        users[username]=pwd
        
    return {f"{username}:{pwd} added"}

# Test request
@api.get('/test/read_db_quest', name="Debug endpoint",tags=['Testing area'],responses=responses)
def get_users():
    return db_quest.to_json()


@api.get('/test/header', name='Get custom header',tags=['Testing area'],responses=responses)
def get_content(custom_header: Optional[str] = Header(Required, description='My own personal header')):
    """returns a custom header
    """
    print(custom_header)
    return {
        'Custom-Header': custom_header
    }
   

# ===========================================================================================================================
# =                                                Debug WORLD !!!!!                                                        =
# ===========================================================================================================================

if __name__ == '__main__':

    # Read the "database"
    db_quest = pd.read_csv(filepath_or_buffer = "./DB/questions.csv")

    # Debug only
    print(db_quest.head())
    print(db_quest.to_json())


    # @app.get("/")
    # async def root():
    #     return {"message": "Hello World"}

# Mettre les users dans un .json