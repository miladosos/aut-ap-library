from datetime import datetime

from flask import jsonify, request
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

from app.routes.data_base import *
from app.application import app


def user_book_handler(book_id, user_id):
    if not user_id:
        raise BadRequest("user_id header is missing")
    users = data_base.data["users"]
    user = [user for user in users if user["id"] == user_id]
    if not user:
        raise NotFound("user not found")
    user = user[0]
    books = data_base.data["books"]
    book = [book for book in books if book["id"] == book_id]
    if not book:
        raise NotFound("book id not found")
    book = book[0]
    return user, book


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.get_json().get("user_id")
    user, book = user_book_handler(book_id, user_id)
    if all([user, book]):
        if book["is_reserved"]:
            raise BadRequest("book is already reserved")
        book["is_reserved"] = True
        reserved_time = datetime.now().isoformat(timespec="seconds").replace("T", " ")
        book["reserved_by"] = {'user_id': user_id, 'username': user["username"]}
        user["reserved_books"].append({'book_id': book_id,
                                       'title': book["title"],
                                       'author': book["author"],
                                       'isbn': book["isbn"],
                                       'reserved_time': reserved_time})
        data_base.save_data()
        return jsonify(
            {"book_id": book_id,
             "user_id": request.headers.get("user_id"),
             "reservation_date": reserved_time}, 201
        )


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("userId")
    user, book = user_book_handler(book_id, user_id)
    book["is_reserved"] = False
    book["reserved_by"] = None
    book = [book for book in user["reserved_books"] if book["book_id"] == book_id]
    if not book:
        raise BadRequest('book not found')
    book = book[0]
    user["reserved_books"].remove(book)
    data_base.save_data()
    return jsonify({"message": "Reservation cancelled successfully"})


@app.route("/api/v1/users/<user_id>/reservations", methods=["GET"])
def get_user_reservations(user_id: str):
    requesting_user_id = request.headers.get("userId")
    if not requesting_user_id:
        raise BadRequest("user_id header is missing")
    if user_id != requesting_user_id:
        raise Forbidden("user_id and requesting user_id are not same")
    user, book = user_book_handler(user_id, user_id)
    return jsonify(user["reserved_books"])
