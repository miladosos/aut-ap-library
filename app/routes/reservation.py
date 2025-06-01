from flask import jsonify, request, abort
from app.application import app
from app.data_access import (
    reserve_book, unreserve_book, get_user_reservations
)


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book_route(book_id: str):
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
    payload = request.get_json(force=True)
    user_id = payload.get("user_id")
    if not user_id:
        abort(400, description="user_id body is required")
    success, result = reserve_book(book_id, user_id)
    if not success:
        if result in ['book_not_found', 'user_not_found']:
            abort(404, description="Book or user not found")
        if result == 'already_reserved':
            abort(400, description="Book already reserved")
    return jsonify({"reservation_id": result})


@app.route("/api/v1/books/<book_id>/unreserve", methods=["POST"])
def unreserve_book_route(book_id: str):
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
    payload = request.get_json(force=True)
    user_id = payload.get("user_id")
    if not user_id:
        abort(400, description="user_id body is required")
    success, result = unreserve_book(book_id, user_id)
    if not success:
        if result in ['book_not_found', 'user_not_found']:
            abort(404, description="Book or user not found")
        if result == 'not_reserved_by_user':
            abort(403, description="Book not reserved by this user")
    return jsonify({"message": "Unreserved"})


@app.route("/api/v1/users/<user_id>/reservations", methods = ['POST'])
def get_user_reservations_route(user_id: str):
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
    payload = request.get_json(force=True)
    id = payload.get("user_id")
    if not id:
        abort(400, description="user_id body is required")
    if id != user_id:
        abort(403, description="Forbidden")
    books, error = get_user_reservations(user_id)
    if error == 'user_not_found':
        abort(404, description="User not found")
    return jsonify(books)