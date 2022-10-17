#############################################################################################################################
#                                                            main                                                           #
#############################################################################################################################

# ================================================          Header           ================================================

"""

Title : main.py
Init craft date : 03/10/2022
Handcraft with love and sweat by : Damien Mascheix @Hagzilla
Notes :
    Main script for the dev of my first API with fast API

"""
# ================================================       Optimizations        ================================================

""" 
shh, an idea is growing ^^

Concentrate on the main demand, note on the extras. Excepted if I have time ...

Put all functions and class in utils

See the exercise notice

"""

# ================================================    Modules import     =====================================================

# Classics
import pandas as pd
import random

# Fast api
from fastapi import FastAPI, HTTPException, status
from fastapi import Header, Body, Query, Depends
from pydantic import Required
from pydantic import BaseModel
from typing import Optional, Union

# Security
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# String jobs
import re

# ================================================          Functions / Class          ================================================

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
    responseC: Optional[str] = None 
    responseD: Optional[str] = None 
    remark : Optional[str] = None 

def check_user(credentials: HTTPBasicCredentials = Depends(security)):
    
    """_summary_
    
    This function manage the basic authentification.

    Raises:
        HTTPException: 401 UNAUTHORIZED "Incorrect email or password"

    Returns:
        dict: return a dictionnary where you can find the the credential name and the access level
    """
    # Check user credentials and raise a 401 error if something is wrong
    if (credentials.username not in users.keys()) or not(pwd_context.verify(credentials.password, users[credentials.username]['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # Communicate access level in case of good authentification
    else:
        access_level = users[credentials.username]['access_level']
   
    return {"user_name":credentials.username,"access_level":access_level}

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
    # Here we get a list of all names of the dataframe
    name_list = list(df[var].unique())
    # Here we delete brackets of the list to have a string of names
    name_string = re.sub(r"\[|\]|\'","",str(name_list))
    # We count the requencey of each modality by column
    count_list = []
    for name in name_list:
        count_list.append(len(df.loc[df[var]==name,:]))
    
    return name_list, name_string, count_list, dict(zip(name_list,count_list))

def string_spliter(x, sep=","):
    
    """_summary_

    Args:
        x (string): the entry string that you want to split
        sep (string, optional): The separator. Defaults to ",".

    Returns:
        _type_: _description_
    """
       
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

def access_lvl_check (curr_usr_acc_lvl, access_level_requested):
    
    """_summary_
    
    Access level checker

    Raises:
        HTTPException: 403 FORBIDDEN "Forbidden access"
    """
    
    if curr_usr_acc_lvl != access_level_requested :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden access",
        )

# ================================================          Warfield          ================================================

# ===================== Data loading 

# Load users database with hash
users = {"admin": {"username": "admin",
                   "hashed_password": pwd_context.hash('4dm1N'),
                   "access_level":"administrator"
                   },
         "alice" : {"username" :  "alice",
                    "hashed_password" : pwd_context.hash('wonderland'),
                    "access_level":"user"
                    },
         "bob" : {"username" :  "bob",
                  "hashed_password" : pwd_context.hash('builder'),
                  "access_level":"user"
                  },
         "clementine" : {"username" :  "clementine",
                         "hashed_password" : pwd_context.hash('mandarine'),
                         "access_level":"user"
                         }
         }

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
async def get_health():
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
async def get_quest_batch_rqst(use:str = Query(description=f"Please, choose ONE(!) of these possibilities : {use_name_string}"),
                         subject:str= Query(description=f"Please, choose one or more of these possibilities. Seperate them by a comma (,) : {subject_name_string}"),
                         quest_num:str= Query(description="Please, choose a number of questions (5, 10 or 20)."
                                              "Be carefull about the number choosen because, according to the previous selection concerning use and subject, "
                                              "you may not have all questions requested."
                                              " FOR INFORMATION :"
                                              f" ===> USE question counts {use_dict}"
                                              f" ===> SUBJECT question counts {subject_dict}" ,
                                              regex="5|10|20",
                                              ),
                         user_validation: dict = Depends(check_user)
                         ):
    
    """_summary_
    \n
    Request to produce MCQs of 5, 10 or 20 questions.
    \n
    You specify  the use, the subject and the number of questions (5, 10 or 20) that you want in your MCQ.
    \n
    Acces only granted for identified users.
    \n
    Args:
        \n
        use (string): Use selection for the MCQ.
        \n
        subject (string): Subjects selection for the MCQ. Seperate them by a comma (,).
        \n
        quest_num (string): Number of questions (5, 10 or 20) to return .
    
    Returns:
        \n
        dict:   "Request reminder": A reminder of the request's configuration as sent by the user
                "Warnings": warnings that could have been raised
                'Questions': MCQ as a json shape
       
    """
       
    ##### Access management
    access_lvl_check (user_validation["access_level"], "user")
     
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
        
    if len(quest_num_idx_avail) == 0:
        warnings_msg.append(f"The initial request of {quest_num} questions is not possible. There are no questions available considering your use and subject selection")
    elif quest_num > len(quest_num_idx_avail):
        warnings_msg.append(f"The initial request of {quest_num} questions is not possible. Only {len(quest_num_idx_avail)} are available considering your use and subject selection")

    if len(db_quest_filt) == 0:
        warnings_msg.append(f"The dataset returned is empty !")
    
    return {"Request reminder":{use, subject, quest_num},
            "Warnings":warnings_msg,
            "Questions": db_quest_filt.to_json()}
   
# Admin / Add questions to the base
@api.post('/admin/new_quest', name='Add question to the base',tags=['Administration'],responses=responses)
async def post_content(added_data: quest_struct = Body(None),
                 user_validation: dict = Depends(check_user)):
    
    """_summary_
    \n
    Request to add a question to the question database.
    \n
    You need to specify  all the parameters of the question.
    \n
    Acces only granted for identified administrators.
    \n
    Args:
        \n
        dict:
            question (string) : Question
            subject (string) : Subject of the question
            use (string) : Use of the test
            correct (string) : Correct answer
            responseA (string) : Response A
            responseB (string) : Response B
            responseC (string) : Response C
            responseD (string) : Response D
            remark (string) : Remark
    Returns:
        dict: string message and a sum up what we have added.
    """
        
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
         
    # Create a list to input a new row at the db_quest
    quest_add_list = [added_data.question,
                      added_data.subject,
                      added_data.use,
                      added_data.correct,
                      added_data.responseA,
                      added_data.responseB,
                      added_data.responseC,
                      added_data.responseD,
                      added_data.remark]
    
    # Add the informations to the questions database
    db_quest.loc[len(db_quest.index)] = quest_add_list
    
    return {"Following data have been added to the question base :" : added_data}

# ================================================     Extras request for testing      ================================================

# Test requests
@api.get('/test/read_users', name="Read users credentials from DB",tags=['Testing area'],responses=responses)
async def get_users(user_validation: dict = Depends(check_user)):
    
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
    
    return users

# Test requests
@api.get("/users/show_current_user", name="Show current user logged",tags=['Testing area'],responses=responses)
async def get_current_user(credentials: HTTPBasicCredentials = Depends(security),
                     user_validation: dict = Depends(check_user)):
    
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
    
    return {"username": credentials.username, "password": pwd_context.hash(credentials.password)}

# Test request
@api.get('/test/read_db_quest', name="Read the question's DB",tags=['Testing area'],responses=responses)
async def get_read_db_quest(user_validation: dict = Depends(check_user)):
    
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
    
    return db_quest.to_json()

# Test request
@api.get('/test/read_db_quest_tail', name="Read the question's DB (last 5 rows)",tags=['Testing area'],responses=responses)
async def get_read_db_quest_tail(user_validation: dict = Depends(check_user)):
    
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
    
    return db_quest.tail().to_json()

# Test request
@api.get('/test/db_quest_var_count', name="Count the number of unique value for the selected variable of the question's DB",tags=['Testing area'],responses=responses)
async def get_db_quest_var_count(variable:str,
                           user_validation: dict = Depends(check_user)):
    
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
    
    return get_var_inf (db_quest,variable)

# Test request
@api.get('/test/header', name='Get custom header',tags=['Testing area'],responses=responses)
async def get_header(custom_header: Optional[str] = Header(Required, description='My own personal header'),
               user_validation: dict = Depends(check_user)):
    """returns a custom header
    """
    
    ##### Access management
    access_lvl_check (user_validation["access_level"], "administrator")
    
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