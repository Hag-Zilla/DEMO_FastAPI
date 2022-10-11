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
# ================================================       Optimizations        ================================================

""" 
shh, an idea is growing ^^

Concentrate on the main demand, note on the extras. Excepted if I have time ...

/admin/new_quest : Ensure that the db_quest is saved after each new entries

Delete all lines concerned by : Debug (to delete)

Clean the code concerning commented lines

Check if the code is well commented and also each request !!!

Realize dostrings for each functions !

Add the async prefix when necessary

Put all functions and class in utils

Verify that all functions are used

Customize error codes

Delete unused vars

Finish responses

use or not if mane at the end ?

/quest_batch_rqst manage request entry fault messages 

"""

# ================================================    Modules import     =====================================================

# Classics
import pandas as pd
import os
import json
import random

# Fast api
from fastapi import FastAPI
from fastapi import Header, Body, Query
from pydantic import Required
from pydantic import BaseModel
from typing import Optional, Union

# String jobs
import re

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

# ================================================          Functions / Class          ================================================

# Defning a structure for a row in the DB questions
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


# Defning a structure for a row in the DB questions
class Quest_batch_request(BaseModel):
    """
    Define the structure of a question batch request
    """
    subject: str
    use: str
    quest_num: int


def get_var_inf (df,var):
    """_summary_
    
    Get count of each unique value for a defined variable of a dataframe.

    Args:
        df (pandas.DataFrame): Entry dataframe
        var (string): Target variable

    Returns:
        list : List of names
        list : List of names as a string
        list : Counts by names
        dict: count of each unique value for a defined variable of a dataframe
    """
    
    name_list = list(df[var].unique())
    name_string = re.sub(r"\[|\]|\'","",str(name_list))
    count_list = []
    for name in name_list:
        count_list.append(len(df.loc[df[var]==name,:]))
    
    return name_list, name_string, count_list, dict(zip(name_list,count_list))

def string_spliter(x, sep=None):
    return x.split(sep)
    

def space_stripper (x):
    """_summary_
    This function strip spaces at the begining and at the end of a string
    Args:
        x (string): _description_

    Returns:
        string: a string without spaces at the begining and at the end
        
    """
    return re.sub(r"^\s+|\s+$","",x)

# ================================================          Warfield          ================================================

# ===================== Data loading 

# Load users database
with open('./DB/users.json', 'r') as f:
    users = json.load(f)

# Load questions database
db_quest = pd.read_csv(filepath_or_buffer = "./DB/questions.csv")

# Get some questions database informations
(use_name_list, use_name_string, use_count_list,use_dict) = get_var_inf (db_quest,'use')
(subject_name_list, subject_name_string, subject_count_list,subject_dict) = get_var_inf (db_quest,'subject')

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







# Question batch request
@api.get('/quest_batch_rqst', name="Question batch request",tags=['main'],responses=responses)
def get_quest_batch_rqst(use:str = Query(description=f"Please, choose ONE(!) of these possibilities : {use_name_string}"),
                         subject:str= Query(description=f"Please, choose one or more of these possibilities. Seperate them by a comma (,) : {subject_name_string}"),
                         quest_num:str= Query(description="Please, choose a number of questions (5, 10 or 20)."
                                              "Be carefull about the number choosen because, according to the previous selection concerning use and subject, "
                                              "you may not have all questions requested."
                                              " FOR INFORMATION :"
                                              f" ===> USE question counts {use_dict}"
                                              f" ===> SUBJECT question counts {subject_dict}" ,
                                              regex="5|10|20",
                                              )
                         ):
    """_summary_

    Args:
        use (str): _description_
        subject (str): _description_
        quest_num (int): _description_

    Returns:
        _type_: _description_
    """
    
    ##### Use management 
    
    # We strip spaces to avoid misunderstanding concerning the entered value
    use = space_stripper (use)
    
    # Filter the dataset according to the use
    db_quest_filt = db_quest.loc[db_quest["use"]==use,:].copy()    
    
    ##### subject management.
    
    # Conversion of the string to a list
    subject_requested = string_spliter(subject,sep=',')
    
    # We strip spaces to avoid misunderstanding concerning the entered value
    subject_requested = [space_stripper (i) for i in subject_requested]
    
    # Keep subjects that are in the database   
    subject_target = [i for i in subject_requested if i in subject_name_list]
    
    # Create a list of subjects that are not in the database   
    subject_errors = [i for i in subject_requested if i not in subject_name_list]

    # Filter the dataset according to the valid subjects
    db_quest_filt = db_quest.loc[db_quest["subject"].isin(subject_target),:].copy()  
        
    ##### quest_num management
    
    # Conversion 
    quest_num = int(quest_num)
    
    # Get the indexes of questions
    quest_num_idx_avail = list(db_quest_filt.index)
    
    # quest_num cases management
    if quest_num_idx_avail == 0 :
        pass
    elif quest_num > len(quest_num_idx_avail):
        quest_num_idx_target = random.sample(quest_num_idx_avail, k= len(quest_num_idx_avail))
        db_quest_filt = db_quest_filt.loc[quest_num_idx_target,:].copy()
    elif quest_num <= len(quest_num_idx_avail):
        quest_num_idx_target = random.sample(quest_num_idx_avail, k=quest_num)
        db_quest_filt = db_quest_filt.loc[quest_num_idx_target,:].copy()
     
    ##### Warning message management
    warnings_msg = list()
    if use not in use_name_list:
        warnings_msg.append(f"The use requested ({use}) is not in the database. ")
    if len(subject_errors) > 0:
        warnings_msg.append(f"The following subjects are not in the database : {subject_errors}.")
    if quest_num > len(quest_num_idx_avail):
        warnings_msg.append(f"The initial request of {quest_num} questions is not possible. Only {len(quest_num_idx_avail)} are available considering your use and subject selection")
    if len(db_quest_filt) == 0:
        warnings_msg.append(f"The dataset returned is empty !")

    
    return {"Request reminder":{use, subject, quest_num},
            "Warnings":warnings_msg,
            'Questions': db_quest_filt.to_json()}
   

# Admin / Add questions to the base
@api.post('/admin/new_quest', name='Add question to the base',tags=['Administration'],responses=responses)
def post_content(added_data: quest_struct = Body(None)):
    
    # Debug (to delete)
    print(type(added_data))
    print(added_data)
    print(added_data.dict())  
    
    # Create a list to input a new row at the db_quest
    quest_add_list = [added_data.question,
                      added_data.subject,
                      added_data.use,
                      added_data.correct,
                      added_data.responseA,
                      added_data.responseB,
                      added_data.responseD ,
                      added_data.responseD,
                      added_data.remark]
    
    # Debug (to delete)
    print(quest_add_list)
    
    db_quest.loc[len(db_quest.index)] = quest_add_list
    
    # Debug (to delete)
    print(db_quest.tail())
    
    return {"Following data have been added to the question base :" : added_data}


#  ========================================================================================================================


# Test requests
@api.get('/test/read_users', name="Read users credentials from DB",tags=['Testing area'],responses=responses)
def get_users():
    return users

# Test requests
@api.post('/test/wright_users', name="Add users credentials to DB",tags=['Testing area'],responses=responses)
def post_add_users(username:str,pwd:str):

    if username not in users.keys():
        users[username]=pwd
        
    return {f"{username}:{pwd} added"}

# Test request
@api.get('/test/read_db_quest', name="Read the question's DB",tags=['Testing area'],responses=responses)
def get_read_db_quest():
    return db_quest.to_json()

# Test request
@api.get('/test/read_db_quest_tail', name="Read the question's DB (last 5 rows)",tags=['Testing area'],responses=responses)
def get_read_db_quest_tail():
    return db_quest.tail().to_json()

# Test request
@api.get('/test/db_quest_var_count', name="Count the number of unique value for the selected variable of the question's DB",tags=['Testing area'],responses=responses)
def get_db_quest_var_count(variable:str):
    return get_var_inf (db_quest,variable)

# Test request
@api.get('/test/header', name='Get custom header',tags=['Testing area'],responses=responses)
def get_header(custom_header: Optional[str] = Header(Required, description='My own personal header')):
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

