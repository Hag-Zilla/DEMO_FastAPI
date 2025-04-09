<div align="center">

# Lite demo about FastAPI 

</div>

---
## Context
---

Welcome to this lite demo about FastAPI. We will treat a short, simple and fictitious use case of personal expense tracking API. The purpose of this repo is to show how to build a simple API with FastAPI.

---
## Overview
---

The Personal Expense Tracking API allows users to manage their expenses efficiently by categorizing them and tracking against a monthly budget. This API provides functionalities for adding, updating, and deleting expenses, setting a global monthly budget, generating alerts for budget overruns, and producing detailed reports.

---
## Key Features
---

### Expense Management

- **Add, Update, and Delete Expenses**: Users can manage their expenses, each of which includes a description, amount, date, and category.
- **Expense Categories**: The API supports the following 15 categories:
  1. **Food**: Grocery shopping expenses.
  2. **Transportation**: Public transport costs, fuel, vehicle maintenance.
  3. **Housing**: Rent, mortgage, utilities.
  4. **Utilities**: Electricity, water, gas, internet.
  5. **Health**: Medical fees, medications, health insurance.
  6. **Leisure**: Recreational activities, outings, cinema.
  7. **Dining Out**: Meals at restaurants, fast food.
  8. **Clothing**: Purchase of clothes and accessories.
  9. **Education**: Tuition fees, books, school supplies.
  10. **Travel**: Airfare, accommodation, tourist activities.
  11. **Savings and Investments**: Contributions to savings or investment accounts.
  12. **Insurance**: Auto, home, life insurance.
  13. **Entertainment**: Streaming subscriptions, video games.
  14. **Gifts and Donations**: Gifts, donations to charitable causes.
  15. **Miscellaneous**: Various expenses not classified elsewhere.

### Monthly Budget Management

- **Set a Global Monthly Budget**: Each user can set a total monthly budget applicable to all categories.
- **Automatic Update**: The monthly budget is updated with each expense addition.
- **Expense Tracking**: Calculate total expenses and compare them with the set budget.

### User Alerts

- **Alert Endpoint**: Checks each user's expenses and identifies those who have exceeded their monthly budget.
- **Cron Job Script**: An external script calls this endpoint to retrieve alerts to be sent.
- **Notification**: Alerts can be sent via email or SMS. (Not treated in this project, but the endpoint is ready)

### Reports

- **Monthly Reports**: Generate a report of expenses for each past month, by category.
- **Period Reports**: Allow users to generate reports for custom periods.
- **User Reports**: Administrators can generate reports for all users.

### Administrative Features

- **User Management**: Administrators can create, update, and delete user accounts.
- **Report Access**: Administrators can access expense reports for all users.

---
## Implementation
---

### Expense Endpoints

- Add, update, and delete expenses.
- Update the monthly budget with each expense addition.

### Budget Endpoints

- Set and update the global monthly budget.

### Alert Endpoint

- Check expenses and generate alerts for users who have exceeded their budget.

### Report Endpoints

- Generate monthly and period reports for users.
- Administrators can generate reports for all users.

### Administrative Endpoints

- Manage users (create, update, delete).
- Access reports for all users.

With this structure, you can create a robust API for personal expense tracking.




---
## Set up
---


### Environment

To set up the environment for this application, you need to run the `setup.sh` script. This script will handle the creation of the necessary environment using either Conda or venv.

1. Run the setup script in you command prompt (CLI): ```bash setup.sh```

2. Choose the Environment Manager: The script will prompt you to choose between Conda and venv. Enter conda or venv as per your preference.

3. Follow the Instructions: The script will guide you through the process of setting up the environment, including installing dependencies.  

### Start the API
Start the API in your CLI, navigate to the project directory and enter the following command to start the API: ```uvicorn main:api --reload```

Here, we specify the main file and the name of the API to launch inside this file: api. The `--reload` argument allows the API to automatically update when making changes to the source file.

Go to http://localhost:8000/ or http://127.0.0.1:8000/ to access the server.

### API Structure

You will find three main points:

- Main: Where you can find the health checker request and a request to build your MCQ after logging in as a user.
- Administration: Where you can find a request that allows you to add questions to the database after logging in as an administrator.
- Testing Area: Extra requests for debugging and tests after logging in as an administrator.

### Requests Documentation

For the documentation, we use the OpenAPI (formerly Swagger) interface. This interface makes it easy to see the endpoints and accepted methods. It also provides curl requests associated with the try.

Go to http://localhost:8000/docs or http://127.0.0.1:8000/docs Or Go to http://localhost:8000/redoc or http://127.0.0.1:8000/redoc

Here you can access the requests and their documentations.

### Other information

### FastAPI on Conda
To install FastAPI on conda
https://anaconda.org/conda-forge/fastapi

### FastAPI documentation
https://fastapi.tiangolo.com/tutorial/first-steps/

### FastAPI basic authentification
https://fastapi.tiangolo.com/advanced/security/http-basic-auth/
