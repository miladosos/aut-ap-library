# Library Management System

A simple library management system built with Flask that allows users to manage books and handle book reservations.

## Table of Contents

- [Features](#features)
- [Learning Objectives](#learning-objectives)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Data Storage](#data-storage)
- [API Documentation](#api-documentation)
  - [Base URL](#base-url)
  - [Authentication](#authentication)
  - [API Endpoints](#api-endpoints)
  - [Request/Response Examples](#requestresponse-examples)
- [Using Swagger Documentation](#using-swagger-documentation)
- [Notes](#notes)

## Features

- Book Management (Create, Read, Delete)
- User Management (Create, Read, Update)
- Book Reservation System
- Simple JSON-based storage
- OpenAPI/Swagger Documentation

## Learning Objectives

This project is designed to help students learn and practice:

1. **Backend Development**

   - RESTful API design and implementation
   - HTTP methods and status codes
   - Request/response handling
   - Data validation and error handling

2. **Flask Framework**

   - Route handling and blueprints
   - Request processing
   - Response formatting
   - Application structure

3. **Testing**

   - Unit testing with pytest
   - API endpoint testing
   - Test organization and structure
   - Mocking and test fixtures

4. **API Documentation**

   - OpenAPI/Swagger specification
   - API endpoint documentation
   - Request/response schema documentation
   - Interactive API testing

5. **Project Structure**

   - Python package organization
   - Module separation
   - Code reusability
   - Clean code practices

6. **Data Management**
   - JSON data handling
   - CRUD operations
   - Data persistence
   - State management

## Prerequisites

- Python 3.x
- uv (Python package installer)
- Flask

## Installation

1. Install uv (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:

```bash
git clone <repository-url>
cd library
```

3. Create and activate virtual environment using uv:

```bash
uv venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

4. Install dependencies:

```bash
uv sync
```

## Project Structure

```
library/
├── README.md
├── main.py                 # Application entry point
├── pyproject.toml         # Project configuration
├── swagger.yaml           # API documentation
├── db.json               # JSON-based database
├── app/                  # Application package
│   ├── __init__.py
│   ├── application.py    # Application factory
│   └── routes/          # Route handlers
│       ├── __init__.py
│       ├── books.py     # Book management routes
│       ├── users.py     # User management routes
│       └── reservation.py # Book reservation routes
├── tests/               # Test suite
│   ├── __init__.py
│   ├── test_books.py
│   ├── test_users.py
│   └── test_reservations.py
└── .venv/              # Virtual environment (not tracked in git)
```

## Running the Application

1. Start the Flask server:

```bash
python app.py
```

2. The application will be available at `http://localhost:8080`

## Running Tests

```bash
uv run python -m pytest
```

## Data Storage

The application uses a `db.json` file as both its database and sample data. This file contains two main sections:

- `users`: Stores user information
- `books`: Stores book information

Important notes about data storage:

- No additional database setup is required
- The `db.json` file serves as both the sample data and the database
- All operations (create, update, delete) will modify this file directly
- Make sure to keep a backup of this file if you want to preserve your data
- The file is automatically updated with every operation that modifies data

## API Documentation

The API is documented using OpenAPI/Swagger specification. You can find the complete API documentation in `swagger.yaml`. The documentation includes:

- Detailed endpoint descriptions
- Request/response schemas
- Authentication requirements
- Error responses
- Example requests and responses

### Base URL

All API endpoints are prefixed with: `http://localhost:8080/api/v1`

### Authentication

The API uses a simple header-based authentication:

- Header: `user_id`
- Required for: Book reservations and user-specific operations

### API Endpoints

#### Books API

| Method | Endpoint      | Description      | Headers Required | Request Body | Response        |
| ------ | ------------- | ---------------- | ---------------- | ------------ | --------------- |
| GET    | `/books`      | List all books   | None             | None         | List of books   |
| GET    | `/books/{id}` | Get book details | None             | None         | Book details    |
| POST   | `/books`      | Create new book  | None             | Book details | Created book    |
| DELETE | `/books/{id}` | Delete a book    | None             | None         | Success message |

#### Users API

| Method | Endpoint      | Description      | Headers Required | Request Body         | Response      |
| ------ | ------------- | ---------------- | ---------------- | -------------------- | ------------- |
| GET    | `/users`      | List all users   | None             | None                 | List of users |
| GET    | `/users/{id}` | Get user details | None             | None                 | User details  |
| POST   | `/users`      | Create new user  | None             | User details         | Created user  |
| PUT    | `/users/{id}` | Update user      | None             | Updated user details | Updated user  |

#### Reservations API

| Method | Endpoint                   | Description             | Headers Required | Request Body | Response               |
| ------ | -------------------------- | ----------------------- | ---------------- | ------------ | ---------------------- |
| GET    | `/users/{id}/reservations` | Get user's reservations | user_id          | None         | List of reserved books |
| POST   | `/books/{id}/reserve`      | Reserve a book          | user_id          | None         | Reservation details    |
| DELETE | `/books/{id}/reserve`      | Cancel a reservation    | user_id          | None         | Success message        |

### Request/Response Examples

#### Book Object

```json
{
  "id": "1",
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "isbn": "978-0743273565",
  "is_reserved": false,
  "reserved_by": null
}
```

#### User Object

```json
{
  "id": "1",
  "username": "john_doe",
  "name": "John Doe",
  "email": "john@example.com",
  "reserved_books": []
}
```

## Using Swagger Documentation

The API documentation is available in Swagger/OpenAPI format. Here's how to use it:

1. **Viewing the Documentation**:

   - Open `swagger.yaml` in a text editor to view the raw specification
   - For a better experience, use an online Swagger editor:
     - Visit [Swagger Editor](https://editor.swagger.io/)
     - Copy and paste the contents of `swagger.yaml`
     - The documentation will be rendered in an interactive format

2. **Interactive Testing**:

   - In the Swagger Editor, you can:
     - View all available endpoints
     - See request/response schemas
     - Test API endpoints directly from the interface
     - View example requests and responses

3. **Understanding the Documentation**:

   - Each endpoint is documented with:
     - HTTP method (GET, POST, PUT, DELETE)
     - Path parameters
     - Query parameters
     - Request body schema
     - Response schemas
     - Authentication requirements
     - Example values

4. **Using the Documentation**:

   - Click on any endpoint to expand its details
   - Use the "Try it out" button to test endpoints
   - Fill in the required parameters
   - Execute the request and view the response
   - Copy the generated curl command for use in your application

5. **Common Sections**:
   - `/books`: Book management endpoints
   - `/users`: User management endpoints
   - `/reservations`: Book reservation endpoints

Note: When testing endpoints that require authentication, make sure to include the `user_id` header in your requests.

## Notes

- The application runs on `localhost:8080`
- No authentication is required, but users must provide their `user_id` in the request headers
- The system prevents deletion of reserved books
- All endpoints are prefixed with `/api/v1`
- For detailed API documentation, refer to `swagger.yaml`
