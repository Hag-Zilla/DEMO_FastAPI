from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import secrets

api = FastAPI()
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {

    "daniel": {
        "username": "daniel",
        "hashed_password": pwd_context.hash('datascientest'),
        "access_level":"administrator"
    },

    "john" : {
        "username" :  "john",
        "hashed_password" : pwd_context.hash('secret'),
        "access_level":"user"
    }

}



def check_user(credentials: HTTPBasicCredentials = Depends(security)):
    
    if (credentials.username not in users.keys()) or not(pwd_context.verify(credentials.password, users[credentials.username]['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        access_level = users[credentials.username]['access_level']
   
    return {"user_name":credentials.username,"access_level":access_level}



@api.get("/users/test1")
def get_try_check_user(test_var_sup:str,user_validation: dict = Depends(check_user)):
    
    access_level_requested = "administrator"
    
    if user_validation["access_level"] != access_level_requested :
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden access",
        )
    
    return {"ça biche !"}



@api.get("/users/show_current")
def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    return {"username": credentials.username, "password": pwd_context.hash(credentials.password)}