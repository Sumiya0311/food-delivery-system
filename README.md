Food Delivery System API

Project Overview

A backend REST API built with FastAPI for managing a food delivery platform. It supports authentication, restaurants, menus, carts, orders, delivery partners, order tracking, and notifications.

Features

- User authentication and role-based access
- Restaurant and menu management
- Address and cart management
- Order creation and order history
- Delivery partner assignment and delivery status updates
- Delivery OTP verification and COD payment tracking
- Live order updates using WebSockets
- Ratings and notifications
- Email testing through Mailtrap Sandbox
- Automated service tests

Technologies Used

- Python
- FastAPI
- SQLAlchemy
- MySQL
- Pydantic
- Uvicorn
- JWT authentication
- WebSockets
- Mailtrap SMTP
- Pytest

Project Setup

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_URL
cd food_delivery_system

2. Create and activate a virtual environment

python -m venv venv
venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Copy ".env.example" to ".env" and enter your own database and SMTP configuration values.

Never commit ".env" or real credentials to GitHub.

5. Create the MySQL database

Create the database specified in your ".env" configuration. Configure the database user and password before running the application.

6. Start the API

uvicorn app.main:app --reload

API Documentation

When the server is running, open:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/

Run Service Tests

python -m pytest tests/test_services.py -v

Compile Check

python -m compileall app

Email Testing

The project uses Mailtrap Sandbox to test email sending. Test messages are captured in the Sandbox inbox and are not delivered to real recipients.

Security Notes

- Keep database and SMTP credentials in ".env".
- Commit ".env.example" with placeholder values only.
- Use appropriate role permissions when accessing protected endpoints.
- Do not publish access tokens or passwords in screenshots.

Project Status

The API startup, health-check endpoint, Mailtrap test email, and 10 service tests have been verified. Review all assignment requirements and endpoint permissions before final submission.