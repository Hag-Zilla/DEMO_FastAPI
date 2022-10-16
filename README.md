
A TRAITER !!!!

XXXXXXXXXXXXXXXX
Ajouter la doc du dataset
Ajouter la doc du json des users
Ajouter la structure des dossiers
créer un fichier requirement.txt pour les utilisateurs de pip
Compléter la doc
renomer le dossier ainsi que l'env (pas train_DST_FastAPI_full)



# train_DST_FastAPI_full

## Set up

### Environment
Please, install the environment associated to this application

    conda env create -f environment.yml

### Start datas DB
The DB will be replaced by a csv file. To download it :

    wget https://dst-de.s3.eu-west-3.amazonaws.com/fastapi_fr/questions.csv

It must be downloaded here : ./DB

### Users DB
Users credentials are stored in the main.py (It is a bad practice but just for the demo :) )

### API start
In your CLI, place you in the "train_DST_FastAPI_full" folder then enter the command line below :

    uvicorn main:api --reload 

Here, we specify the main file and the name of the API to launch inside this file: api. The --reload argument allows to automatically update the API when making changes to the source file.

Go to http://localhost:8000/ or http://127.0.0.1:8000/ to access the server.

### OpenAPI documentation
OpenAPI (formerly Swagger) interface. This interface makes it easy to see the endpoints and accepted methods. It also give curl request assiciated to the try.

Go to http://localhost:8000/docs or http://127.0.0.1:8000/docs
Or
Go to http://localhost:8000/redoc or http://127.0.0.1:8000/redoc

Here you can access to the request and there documentations.

## Others informations

### FastAPI documentation
https://fastapi.tiangolo.com/tutorial/first-steps/

To install FastAPI on conda
https://anaconda.org/conda-forge/fastapi



