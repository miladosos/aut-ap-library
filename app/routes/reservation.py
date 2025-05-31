from datetime import datetime

from flask import jsonify, request

from app.application import app
from database import db

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    """
    Reserve a book for a user

    Args:
        book_id (str): The id of the book to reserve

    Returns:
        dict: Reservation details

    Raises:
        BadRequest: If user_id header is missing or book is already reserved
        NotFound: If the book or user is not found
    """
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id header"}), 400

    books = db.data.get('books', [])
    users = db.data.get('users', [])

    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if book.get("reserved_by"):
        return jsonify({"error": "Book is already reserved"}), 400

    book["reserved_by"] = user_id
    book["reserved_at"] = datetime.now()
    db.save()

    return jsonify({
        "book_id": book_id,
        "reserved_by": user_id,
        "reserved_at": book["reserved_at"]
    }), 201

    


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    """
    Cancel a book reservation

    Args:
        book_id (str): The id of the book to cancel reservation

    Returns:
        dict: Success message

    Raises:
        BadRequest: If user_id header is missing or book is not reserved by user
        NotFound: If the book is not found
    """
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id header"}), 400

    books = db.data.get('books', [])
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    if book.get("reserved_by") != user_id:
        return jsonify({"error": "Book is not reserved by this user"}), 400

    book["reserved_by"] = None
    book["reserved_at"] = None
    db.save()
    return jsonify({"message": "Reservation cancelled successfully"})


@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    """
    Get all reservations for a user

    Args:
        user_id (str): The id of the user

    Returns:
        list: List of reserved books

    Raises:
        BadRequest: If user_id header is missing
        NotFound: If the user is not found
        Forbidden: If requesting user is not the same as target user
    """
    requesting_user_id = request.headers.get("user_id")
    if not requesting_user_id:
        return jsonify({"error": "Missing user_id header"}), 400

    if requesting_user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403

    users = db.data.get('users', [])
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    books = db.data.get('books', [])
    reserved_books = [
        {
            "book_id": b["id"],
            "title": b.get("title"),
            "reserved_at": b.get("reserved_at")
        }
        for b in books if b.get("reserved_by") == user_id
    ]

    return jsonify(reserved_books)
