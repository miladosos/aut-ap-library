import json

import pytest

from app.application import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_get_all_books(client):
    """Test getting all books"""
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_book_by_id(client):
    """Test getting a specific book by ID"""
    # Test with existing book
    response = client.get("/api/v1/books/1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["id"] == "1"
    assert "title" in data
    assert "author" in data

    # Test with non-existing book
    response = client.get("/api/v1/books/999")
    assert response.status_code == 404


def test_create_book(client):
    """Test creating a new book"""
    new_book = {"title": "Test Book", "author": "Test Author", "isbn": "1234567890"}
    response = client.post("/api/v1/books", data=json.dumps(new_book), content_type="application/json")
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data["title"] == new_book["title"]
    assert data["author"] == new_book["author"]
    assert data["isbn"] == new_book["isbn"]
    assert "id" in data


def test_create_book_invalid_data(client):
    """Test creating a book with invalid data"""
    invalid_book = {
        "title": "Test Book"
        # Missing required fields
    }
    response = client.post("/api/v1/books", data=json.dumps(invalid_book), content_type="application/json")
    assert response.status_code == 400


def test_delete_book(client):
    """Test deleting a book"""
    # First create a book
    new_book = {"title": "Book to Delete", "author": "Test Author", "isbn": "9876543210"}
    create_response = client.post("/api/v1/books", data=json.dumps(new_book), content_type="application/json")
    book_id = json.loads(create_response.data)["id"]

    # Then delete it
    response = client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 200

    # Verify it's deleted
    get_response = client.get(f"/api/v1/books/{book_id}")
    assert get_response.status_code == 404


def test_delete_reserved_book(client):
    """Test deleting a book that is currently reserved"""
    # First create a book
    new_book = {"title": "Test Book", "author": "Test Author", "isbn": "1234567890"}
    response = client.post("/api/v1/books", data=json.dumps(new_book), content_type="application/json")
    assert response.status_code == 201
    book_id = json.loads(response.data)["id"]

    # Create a user
    new_user = {"username": "testuser1", "name": "Test User", "email": "test@example.com"}
    response = client.post("/api/v1/users", data=json.dumps(new_user), content_type="application/json")
    assert response.status_code == 201
    user_id = json.loads(response.data)["id"]

    # Reserve the book
    response = client.post(f"/api/v1/books/{book_id}/reserve", headers={"user_id": user_id})
    assert response.status_code == 200

    # Try to delete the reserved book
    response = client.delete(f"/api/v1/books/{book_id}")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "reserved" in data["error"].lower()