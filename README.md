# train_DST_FastAPI_full

## Set up

### Environment
Please, install the environment associated to this program

    conda env create -f environment.yml

### API start
Enter the commande line below in your CLI :

    uvicorn main:api --reload 

Here, we specify the main file and the name of the API to launch inside this file: api. The --reload argument allows to automatically update the API when making changes to the source file.

Go to http://localhost:8000/ or http://127.0.0.1:8000/

### Database
The DB will be replaced by a csv file. To download it :
    wget https://dst-de.s3.eu-west-3.amazonaws.com/fastapi_fr/questions.csv

## Others informations

### OpenAPI documentation
OpenAPI (formerly Swagger) interface. This interface makes it easy to see the endpoints and accepted methods. It also give curl request assiciated to the try.

Go to http://localhost:8000/docs or http://127.0.0.1:8000/docs
Or
Go to http://localhost:8000/redoc or http://127.0.0.1:8000/redoc

To install FastAPI on conda
https://anaconda.org/conda-forge/fastapi