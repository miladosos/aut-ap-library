import json

import pytest
from app.application import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_all_users(client):
    """Test getting all users"""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_user_by_id(client):
    """Test getting a specific user by ID"""
    # Test with existing user
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == "1"
    assert "username" in data
    assert "name" in data
    assert "email" in data

    # Test with non-existing user
    response = client.get("/api/v1/users/999")
    assert response.status_code == 404


def test_create_user(client):
    """Test creating a new user"""
    new_user = {"username": "testuser", "name": "Test User", "email": "test@example.com"}
    response = client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["username"] == new_user["username"]
    assert data["name"] == new_user["name"]
    assert data["email"] == new_user["email"]
    assert "id" in data
    assert "reserved_books" in data
    assert isinstance(data["reserved_books"], list)


def test_create_user_invalid_data(client):
    """Test creating a user with invalid data"""
    invalid_user = {
        "username": "testuser"
        # Missing required fields
    }
    response = client.post("/api/v1/users", data=json.dumps(invalid_user), content_type="application/json")
    assert response.status_code == 400


def test_create_user_duplicate_username(client):
    """Test creating a user with duplicate username"""
    # First create a user
    new_user = {"username": "duplicateuser", "name": "Test User", "email": "test@example.com"}
    client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")

    # Try to create another user with same username
    response = client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_update_user(client):
    """Test updating a user"""
    # First create a user
    new_user = {"username": "updatetest", "name": "Update Test", "email": "update@example.com"}
    create_response = client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")
    user_id = json.loads(create_response.data)["id"]

    # Update the user
    updated_data = {"name": "Updated Name", "email": "updated@example.com"}
    response = client.put(f"/api/v1/users/{user_id}", data=json.dumps(updated_data), content_type="application/json")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == updated_data["name"]
    assert data["email"] == updated_data["email"]
    assert data["username"] == new_user["username"]  # Username shouldn't change


def test_update_nonexistent_user(client):
    """Test updating a non-existent user"""
    updated_data = {"name": "Updated Name", "email": "updated@example.com"}
    response = client.put("/api/v1/users/999", data=json.dumps(updated_data), content_type="application/json")
    assert response.status_code == 404


def test_get_user_reservations(client):
    """Test getting user's reservations"""
    # First create a user
    new_user = {"username": "reservetest", "name": "Reserve Test", "email": "reserve@example.com"}
    create_response = client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")
    user_id = json.loads(create_response.data)["id"]

    # Get user's reservations
    response = client.get(f"/api/v1/users/{user_id}/reservations")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
