from datetime import datetime

from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from app.application import app

import os
import json


current_dir = os.path.dirname(__file__)

db_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'db.json'))

with open(db_path, 'r') as file:
    DATABASE = json.load(file)

def commit():
    with open(db_path, 'w') as f:
        json.dump(DATABASE, f)

def get_book(book_id):
    for book in DATABASE['books']:
        if book['id'] == book_id:
            return book
    return None


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

    try:
        try:
            user_id = request.headers.get("user_id")
        except BadRequest:
            raise BadRequest("User_id header is missing")

        my_user = None
        for user in DATABASE["users"]:
            if user["id"] == user_id:
                my_user = user

        if my_user is None:
            raise NotFound("user is not found")

        for book in DATABASE["books"]:
            if book["id"] == book_id:
                if book["is_reserved"]:
                    raise BadRequest("Book already reserved")

                book["is_reserved"] = True
                book["reserved_by"] = my_user["id"]
                my_user["reserved_books"].append(book["id"])
                commit()

                return jsonify(
                    {"book_id": book_id, "user_id": request.headers.get("user_id"), "reservation_date": datetime.now().isoformat()}
                )

        raise NotFound("book is not found")

    except BadRequest as e:
        raise BadRequest(str(e))


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

    try:
        try:
            user_id = request.headers.get("user_id")
        except BadRequest:
            raise BadRequest("User_id header is missing")

        my_user = None
        for user in DATABASE["users"]:
            if user["id"] == user_id:
                my_user = user

        if my_user is None:
            raise NotFound("user is not found")

        for book in DATABASE["books"]:
            if book["id"] == book_id:
                if book["reserved_by"] != my_user["id"]:
                    raise BadRequest("Book is not reserved by user")

                book["is_reserved"] = False
                book["reserved_by"] = None
                my_user["reserved_books"].remove(book["id"])
                commit()

                return jsonify({"message": "Reservation cancelled successfully"})

        raise NotFound("book is not found")

    except BadRequest as e:
        raise BadRequest(str(e))


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

    try:
        try:
            user_id = request.headers.get("user_id")
        except BadRequest:
            raise BadRequest("User_id header is missing")

        my_user = None
        for user in DATABASE["users"]:
            if user["id"] == user_id:
                my_user = user

        if my_user is None:
            raise NotFound("user is not found")
        if my_user["id"] != user_id:
            raise Forbidden("user is not the same as target user")

        books = list()
        for book_id in my_user["reserved_books"]:
            book = get_book(book_id)
            if book:
                books.append(book)

        return jsonify(books)

    except BadRequest as e:
        raise BadRequest(str(e))
