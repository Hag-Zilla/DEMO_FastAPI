<div align="center">

# Lite Demo About FastAPI

</div>

---

## Context

---

Welcome to this lite demo about FastAPI. We will treat a short, simple, and fictitious use case of a personal expense tracking API. The purpose of this repo is to show how to build a simple API with FastAPI.

---

## Overview

---

The Personal Expense Tracking API allows users to manage their expenses efficiently by categorizing them and tracking against a monthly budget. This API provides functionalities for adding, updating, and deleting expenses, setting a global monthly budget, generating alerts for budget overruns, and producing detailed reports.

---

## Key Features

---

### Expense Management

- **Add, Update, and Delete Expenses**: Authenticated users can add new expenses, update existing ones, and delete expenses as needed. Each expense is recorded with details such as description, amount, date, and category. Each expense is linked to the user who created it using the `user_id` foreign key, allowing for personalized expense tracking.

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

- **Set a Global Monthly Budget**: Users can set a global monthly budget that applies to all expense categories. This budget is stored in the `users` table.
- **Updating the Budget**: With each expense addition, the user's remaining budget is automatically updated to reflect the remaining amount for the month.
- **Expense Tracking**: Calculate total expenses and compare them with the set budget.

### User Management

- **Creating Users**: Users can be created via the `/users/` endpoint, which accepts a username, password, and budget. The user data is stored in the `users` table.
- **Authentication**: User authentication is handled using OAuth2 with password hashing for security. The authenticated user can perform actions like adding expenses.

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

## Endpoints

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

### Main Endpoints

- **Health Check**: A simple endpoint to verify the API's health.
  - **Endpoint**: `/health`
  - **Method**: `GET`
  - **Description**: Returns the current state of the API.
  - **Response**: `{ "state": "API is currently running. Please proceed" }`

With this structure, you can create a robust API for personal expense tracking.

---

## Database

---

The Personal Expense Tracking API utilizes **SQLite** as its database solution, providing a lightweight and efficient way to manage user data and expenses. Below is an overview of how SQLite is integrated and operated within the project:

### Integration with FastAPI

1. **Setup and Configuration**:
   - SQLite is used as the database engine, and SQLAlchemy is employed as the Object-Relational Mapping (ORM) tool to interact with the database.
   - The database file (`expense_tracker.db`) is created in the project directory, making it easy to manage and deploy.

2. **Database Models**:
   - **User Model**: Represents a user with fields for `id` (primary key), `username`, `hashed_password`, and `budget`. This model stores user credentials and their monthly budget.
   - **Expense Model**: Represents an expense entry with fields for `id` (primary key), `description`, `amount`, `date`, `category`, and `user_id` (foreign key linking to the `User` model). This model stores individual expense records.

3. **Database Initialization**:
   - The database and its tables are automatically created when the application starts. SQLAlchemy handles the creation of tables based on the defined models.
   - The `Base.metadata.create_all(bind=engine)` command ensures that the necessary schema is in place.

### Database Schema

The database schema consists of two primary tables: `users` and `expenses`.

- **Users Table**:
  - `id` (INTEGER, PRIMARY KEY): A unique identifier for each user.
  - `username` (STRING, UNIQUE): The username of the user, which must be unique.
  - `hashed_password` (STRING): The hashed password for the user, ensuring security.
  - `budget` (FLOAT): The global monthly budget set by the user, applicable to all expense categories.

- **Expenses Table**:
  - `id` (INTEGER, PRIMARY KEY): A unique identifier for each expense entry.
  - `description` (STRING): A brief description of the expense.
  - `amount` (FLOAT): The amount spent for the expense.
  - `date` (STRING): The date when the expense was incurred.
  - `category` (STRING): The category of the expense (e.g., Food, Transportation).
  - `user_id` (INTEGER, FOREIGN KEY): A reference to the `id` field in the `users` table, indicating the user who created the expense.

### Benefits of Using SQLite

- **Simplicity**: SQLite requires no server setup or complex configuration, making it easy to integrate and use.
- **Efficiency**: SQLite is designed to be efficient for most read and write operations, making it suitable for small to medium-sized applications.
- **Portability**: The entire database is contained in a single file, making it easy to move, backup, and deploy.

### Scalability Considerations

- While SQLite is ideal for prototyping and small applications, it can be easily swapped out for more robust database solutions like PostgreSQL or MySQL as your application grows.
- The modular design of the API allows for seamless transition to other database systems with minimal changes to the codebase.

---

## Setup

---

### Environment

To set up the environment for this application, you need to run the `setup.sh` script. This script will handle the creation of the necessary environment using either Conda or venv.

1. Run the setup script in your command prompt (CLI):
   ```bash
   bash setup.sh
   ```

2. Choose the Environment Manager: The script will prompt you to choose between `conda` and `venv`. You can select either

3. Follow the Instructions: The script will guide you through the process of setting up the environment, including installing dependencies.  

### Start the API
Start the API in your CLI, navigate to the project directory and enter the following command to start the API: 
  ```bash
  bash uvicorn main:api --reload
  ```

Here, we specify the main file and the name of the API to launch inside this file: api. The `--reload` argument allows the API to automatically update when making changes to the source file.

Go to http://localhost:8000/ or http://127.0.0.1:8000/ to access the server.

### API Structure

You will find three main points:

- **Main**: Where you can find the health checker request and a request to build your MCQ after logging in as a user.
- **Administration**: Where you can find a request that allows you to add questions to the database after logging in as an administrator.
- **Testing Area**: Extra requests for debugging and tests after logging in as an administrator.

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