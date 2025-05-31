from datetime import datetime
from flask import request, jsonify
from app.application import app
from database import db
from werkzeug.exceptions import BadRequest, NotFound, Forbidden


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
        raise BadRequest

    users = db.get_all_users()
    if user_id not in users:
        raise NotFound(f"{user_id} not found")

    books = db.get_all_books()
    if book_id not in books:
        raise NotFound(f"{book_id} not found")

    book = books[book_id]
    if book.get("reserved", False):
        raise BadRequest

    book["is_reserved"] = True
    book["reserved_by"] = user_id
    book["reservation_date"] = datetime.now().isoformat()

    db.save_books(books)

    return jsonify(
        {"book_id": book_id,
         "user_id": user_id,
         "reservation_date": book["reservation_date"]
         })


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
        raise BadRequest("Missing user_id")

    users = db.get_all_users()
    if user_id not in users:
        raise NotFound("user not found")

    books = db.get_all_books()
    if book_id not in books:
        raise NotFound("book not found")

    book = books[book_id]
    if not book.get("reserved", False) or book.get("reserved_by") != user_id:
        raise BadRequest("book not reserved")

    book["is_reserved"] = False
    book.pop("reserved_by", None)
    book.pop("reservation_date", None)

    db.save_books(books)

    return jsonify({"message": "Reservation cancelled successfully"})


@app.route("/api/v1/users/<user_id>/reservations", methods=["GET"])
def get_user_reservations(user_id: str):
    requester_id = request.headers.get("user_id")
    if not requester_id:
        raise BadRequest("Missing user_id")

    if requester_id != user_id:
        raise Forbidden

    users = db.get_all_users()
    if user_id not in users:
        raise NotFound(f"{user_id} not found")

    books = db.get_all_books()
    reserved_books = []

    for book_id, book in books.items():
        if book.get("reserved_by") == user_id:
            reserved_books.append({
                "id": book_id,
                "title": books[book_id].get("title"),
                "author": books[book_id].get("author"),
                "reserved_by": books[book_id].get("reserved_by"),
                "reservation_date": books[book_id].get("reservation_date")
            })

    return jsonify(reserved_books), 200
