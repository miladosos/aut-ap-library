from datetime import datetime

from flask import jsonify, request
from rdflib.parser import headers
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from app.application import app

from .data_base import *

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
    user_id = request.get_json().get('user_id', None)
    # user_id = request.headers.get('user_id', None)
    if not user_id:
        raise BadRequest('user_id header is missing')

    db = data_base_loder()
    users = db["users"]
    books = db["books"]
    is_book_exists = False
    reserving_book = None
    for book in books:
        if book['id'] == book_id:
            reserving_book = book
            if book["is_reserved"]:
                raise BadRequest('book is already reserved')
            is_book_exists = True
    if not is_book_exists:
        raise NotFound('book not found')


    for user in users:
        if user["id"] == user_id:
            reservations_id = db["reservations_id"]
            reservation_id = 1
            for i in range(1, len(reservations_id) + 2):
                i = str(i)
                if i not in reservations_id:
                    reservation_id = i
                    reservations_id.append(i)
                    db["reservations_id"] = reservations_id
                    break
            user["reserved_books"].append({"book_id":book_id, "reservation_id":reservation_id})
            db["users"] = users
            db["reservations"].append(
                {"id":reservation_id,"book_id": book_id, "user_id": user_id, "reservation_date": datetime.now().isoformat(timespec='seconds').split('T')}
            )
            reserving_book["is_reserved"] = True
            reserving_book["reserved_by"] = {"user_id":user_id, "reservation_id":reservation_id}
            db["books"] = books
            data_base_dumper(db)
            return jsonify(
                {"book_id": book_id, "user_id": request.headers.get("user_id"), "reservation_date": datetime.now().isoformat(timespec='seconds').split('T')}
            )
    raise NotFound("user not found")


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

    db = data_base_loder()
    users = db["users"]
    books = db["books"]
    user_id = None
    reservation_id = None
    is_book_exists = False
    for book in books:
        if book['id'] == book_id:
            if not book["is_reserved"]:
                raise BadRequest('book is not reserved')
            user_id = book["reserved_by"]["user_id"]
            reservation_id = book["reserved_by"]["reservation_id"]
            book["is_reserved"] = False
            book["reserved_by"] = None
            db["books"] = books
            is_book_exists = True
    if not is_book_exists:
        raise NotFound('book not found')

    for user in users:
        if user["id"] == user_id:
            reservations = db["reservations"]
            reservations_id = db["reservations_id"]
            for reservation in user["reserved_books"]:
                if reservation["reservation_id"] == reservation_id:
                    user["reserved_books"].remove(reservation)
            for reservation in reservations:
                if reservation["book_id"] == book_id:
                    reservations_id.remove(reservation_id)
                    reservations.remove(reservation)
            db["reservations_id"] = reservations_id
            db["reservations"] = reservations
            db["users"] = users
            data_base_dumper(db)
            return jsonify({"message": "Reservation cancelled successfully"})
    raise NotFound("user not found")



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
    requesting_user_id = request.get_json().get('user_id', None)
    # requesting_user_id = request.headers.get('user_id', None)
    if not requesting_user_id:
        raise BadRequest('user_id header is missing')
    if not (requesting_user_id == user_id):
        raise Forbidden('user_id and requesting user_id is not the same')
    db = data_base_loder()
    users = db["users"]
    for user in users:
        if user["id"] == user_id:
            return jsonify(user["reserved_books"])
    raise NotFound("user not found")

