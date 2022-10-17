# train_FastAPI_lite_demo
---

## Context

Welcome to this lite demo about FastAPI.

We will treate a short and factice use case as described below :

We will put ourselves in the shoes of a company that creates questionnaires via an application for Smartphone or Web browser. To simplify the architecture of these different products, the company wants to set up an API. The purpose of this is to query a database to return a series of questions.

On the application or the web browser, the user must be able to choose a type of test (use) as well as one or more categories (subject). In addition, the application can produce MCQs of 5, 10 or 20 questions. The API must therefore be able to return this number of questions. As the application must be able to generate many MCQs, the questions must be returned in random order: thus, a query with the same parameters may return different questions.

Since users must have created an account, we must be able to verify their identifiers. For the moment the API uses basic authentication, based on username and password: the character string containing Basic username:password must be passed in the Authorization header.

The API will also need to implement an endpoint to verify that the API is functional. Another functionality must be able to allow an ```admin``` user whose password is ```4dm1N``` to create a new question.

---

## Set up

### Environment
Please, install the environment associated to this application :

    conda env create -f environment.yml

or for a PIP way :

    pip install -r requirements.txt

### Start datas DB
The DB will be replaced by a csv file. To download it :

    wget https://dst-de.s3.eu-west-3.amazonaws.com/fastapi_fr/questions.csv

It must be downloaded here : ./DB

Dataset informations :

    question: The questions
    subject: The question's category
    correct: The liste of correct answers
    use: the MCQ type for which the question is used
    responseA: Answer A
    responseB: Answer B
    responseC: Answer C
    responseD: Answer D (if it exist)
    remark: if needed

### Users DB
Users credentials are stored in the main.py (It is a bad practice but just for the demo :) )

---

## How to use

### API start
In your CLI, place you in the "train_FastAPI_lite_demo" folder then enter the command line below :

    uvicorn main:api --reload 

Here, we specify the main file and the name of the API to launch inside this file: api. The ```--reload``` argument allows to automatically update the API when making changes to the source file.

Go to http://localhost:8000/ or http://127.0.0.1:8000/ to access the server.

### API structure

You will find three main points :

- Main (Where you can find the health checker request and a request to build your MCQ after log in as user)
- Administration (Where you can find a request that allow you to add question to the database after log in as administrator)
- Testing area (They are extra requests for debugging and tests after log in as administrator)

### Requests documentation
For the documentation, we use OpenAPI (formerly Swagger) interface. This interface makes it easy to see the endpoints and accepted methods. It also give curl request assiciated to the try.

Go to http://localhost:8000/docs or http://127.0.0.1:8000/docs
Or
Go to http://localhost:8000/redoc or http://127.0.0.1:8000/redoc

Here you can access to the request and there documentations.

---

## Others informations

### FastAPI on Conda
To install FastAPI on conda
https://anaconda.org/conda-forge/fastapi

### FastAPI documentation
https://fastapi.tiangolo.com/tutorial/first-steps/

### FastAPI basic authentification
https://fastapi.tiangolo.com/advanced/security/http-basic-auth/





