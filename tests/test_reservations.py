import json

import pytest

from app.application import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_book_and_user(client):
    """Fixture to create a book and user for reservation tests"""
    # Create a book
    new_book = {"title": "Reservation Test Book", "author": "Test Author", "isbn": "1234567890"}
    book_response = client.post("/api/v1/books", data=json.dumps(new_book), content_type="application/json")
    book_id = json.loads(book_response.data)["id"]

    # Create a user
    new_user = {"username": "reservetest", "name": "Reserve Test", "email": "reserve@example.com"}
    user_response = client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")
    user_id = json.loads(user_response.data)["id"]

    return {"book_id": book_id, "user_id": user_id}


def test_reserve_book(client, setup_book_and_user):
    """Test reserving a book"""
    book_id = setup_book_and_user["book_id"]
    user_id = setup_book_and_user["user_id"]

    # Reserve the book
    response = client.post(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["book_id"] == book_id
    assert data["user_id"] == user_id
    assert "reservation_date" in data

    # Verify book is marked as reserved
    book_response = client.get(f"/api/v1/books/{book_id}")
    book_data = json.loads(book_response.data)
    assert book_data["is_reserved"] is True
    assert book_data["reserved_by"] == user_id


def test_reserve_already_reserved_book(client, setup_book_and_user):
    """Test reserving a book that's already reserved"""
    book_id = setup_book_and_user["book_id"]
    user_id = setup_book_and_user["user_id"]

    # First reservation
    client.post(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})

    # Try to reserve again
    response = client.post(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_reserve_nonexistent_book(client, setup_book_and_user):
    """Test reserving a non-existent book"""
    user_id = setup_book_and_user["user_id"]

    response = client.post("/api/v1/books/999/reserve", headers={"user_id": user_id})
    assert response.status_code == 404


def test_reserve_book_without_user_id(client, setup_book_and_user):
    """Test reserving a book without providing user_id"""
    book_id = setup_book_and_user["book_id"]

    response = client.post(f"/api/v1/books/{book_id}/reserve")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_cancel_reservation(client, setup_book_and_user):
    """Test canceling a book reservation"""
    book_id = setup_book_and_user["book_id"]
    user_id = setup_book_and_user["user_id"]

    # First reserve the book
    client.post(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})

    # Cancel the reservation
    response = client.delete(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})
    assert response.status_code == 200

    # Verify book is no longer reserved
    book_response = client.get(f"/api/v1/books/{book_id}")
    book_data = json.loads(book_response.data)
    assert book_data["is_reserved"] is False
    assert book_data["reserved_by"] is None


def test_cancel_nonexistent_reservation(client, setup_book_and_user):
    """Test canceling a reservation that doesn't exist"""
    book_id = setup_book_and_user["book_id"]
    user_id = setup_book_and_user["user_id"]

    response = client.delete(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_get_user_reservations(client, setup_book_and_user):
    """Test getting all reservations for a user"""
    book_id = setup_book_and_user["book_id"]
    user_id = setup_book_and_user["user_id"]

    # Reserve a book
    client.post(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})

    # Get user's reservations
    response = client.get(f"/api/v1/users/{user_id}/reservations", headers={"user_id": user_id})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["book_id"] == book_id
    assert data[0]["user_id"] == user_id


def test_get_reservations_for_nonexistent_user(client):
    """Test getting reservations for a non-existent user"""
    response = client.get("/api/v1/users/999/reservations", headers={"user_id": "999"})
    assert response.status_code == 404
