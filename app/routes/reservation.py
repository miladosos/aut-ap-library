from datetime import datetime

from flask import jsonify, request

from app.application import app
from .database import *
from werkzeug.exceptions import NotFound , BadRequest , Forbidden

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    database = load_data()
    books = database["books"]
    users = database["users"]
    
    user_id = request.headers.get("user_id")
    if not user_id:
        raise BadRequest("user_id header is missing")
    
    for book in books :
        if book["id"] == book_id and book["is_reserved"] == False:
            r_book = book
        if not r_book :
            raise BadRequest("book is already reserved")
    
    if not r_book :
        raise NotFound("book not found")
    
    for user in users :
        if user["id"] == user_id :
            r_user = user
    
    if not r_user :
        raise NotFound("user not found")
    
    r_user["reserved_books"].append(f"{r_book}")
    r_book["is_reserved"] = True
    r_book["reserved_by"] = r_user
    
    return jsonify(
        {"book_id": book_id, "user_id": request.headers.get("user_id"), "reservation_date": datetime.now().isoformat()}
    )

    """
    Raises:
        BadRequest: If user_id header is missing or book is already reserved
        NotFound: If the book or user is not found
    """

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    database = load_data()
    users = database["users"]
    books = database["books"]
    
    user_id = request.headers.get("user_id")
    if not user_id:
        raise BadRequest("user_id header is missing")

    for book in books :
        if book["id"] == book_id :
            book["is_reserved"] = False
            book["reserved_by"] = None
        
        if  book["is_reserved"] == False:
            raise BadRequest("Book is not reserved by this user")
    
    for user in users :
        if user_id == user["id"] :
            user["reserved_book"].pop(f"{book}")

    return jsonify({"message": "Reservation cancelled successfully"})

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


@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    database = load_data()
    users = database["users"]

    requesting_user = request.headers.get("user_id")
    if not requesting_user:
        raise BadRequest("Missing user_id header")

    for user in users :
        if user["id"] == user_id :
            reserved_books = user["reserved_books"]
        if not user :
            raise NotFound("user not found")             
    
    if user_id != requesting_user:
        raise Forbidden("You are not allowed to access this user’s reservations")

    return jsonify(reserved_books)
    
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
