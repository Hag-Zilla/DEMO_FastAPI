

# ================================================    Modules import     =====================================================

# Classics
import pandas as pd
import os
import json

# Fast api
from fastapi import FastAPI
from fastapi import Header, Body




# ================================================          Warfield          ================================================

# ==================== API instace
app = Fastapp(title="My first API \m/",
              description="My first API powered by Fastapi.",
              version="1.0.0",
              openapp_tags=[{'name': 'main','description': 'main functions'},
                            {'name': 'quest_mgt','description': 'Questions management'}
                            ]
              )

# ===================== Common responses customization
responses = {200: {"description": "OK"},
             404: {"description": "Item not found"},
             302: {"description": "The item was moved"},
             403: {"description": "Not enough privileges"},
             }

# ===================== Requests management
     


from fastapi import Depends   
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


Faire simple pour l'authentification afin de me concentrer sur le reste.
Une fois fait, j'insérerais l'authentification
Attention, le Header ne supporte pas le mot Authentification !!!!
+voir notes sur cahier
Suivre le tutoriel https://fastapi.tiangolo.com/tutorial/security/first-steps/
et https://fastapi.tiangolo.com/advanced/security/http-basic-auth/

https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization




#  ========================================================================================================================


# Test request
@app.get('/test/read', name="Debug endpoint",tags=['Default'],responses=responses)
def get_users():
    return users

@app.post('/test/wright', name="Debug endpoint",tags=['Default'],responses=responses)
def post_add_users(username:str,pwd:str):

    if username not in users.keys():
        users[username]=pwd
        
    return {f"{username}:{pwd} added"}


@app.get('/test/header', name='Get custom header',tags=['Default'],responses=responses)
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

    # Identifying the parent directory of the script
    curr_script_dir = os.path.dirname(__file__)

    # Read the "database"
    database = pd.read_csv(filepath_or_buffer = curr_script_dir+"/DB/questions.csv")

    # Debug only
    print(database.head())


    # @app.get("/")
    # async def root():
    #     return {"message": "Hello World"}

# Mettre les users dans un .json