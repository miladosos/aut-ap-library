from datetime import datetime

from flask import jsonify, request

from app.application import app
import json
from werkzeug.exceptions import BadRequest, NotFound, Forbidden

class Database:
    def __init__(self):
        with open('db.json', 'r') as file:
            self.db = json.load(file)

    def get_db(self):
        return self.db

    def return_books(self):
        return self.db["books"]

    def return_book(self, id):
        for book in self.db["books"]:
            if book["id"] == str(id):
                return book
        return None

    def return_users(self):
        return self.db["users"]

    def return_user(self, id):
        for user in self.db["users"]:
            if user["id"] == str(id):
                return user
        return None

    def save(self):
        with open('db.json', 'w') as file:
            json.dump(self.db, file, indent=4)


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.headers.get("user_id")
    user = Database().return_user(user_id)
    book = Database().return_book(book_id)

    if not user_id:
        raise BadRequest("Missing user_id in request headers.")
    if not user:
        raise NotFound("User not found.")
    if not book:
        raise NotFound("Book not found.")
    if book.get("reserved_by"):
        raise BadRequest("Book is already reserved.")

    book["reserved_by"] = user_id
    book["reservation_date"] = datetime.now().isoformat()

    Database().save()

    return jsonify({
        "book_id": book_id,
        "user_id": user_id,
        "reservation_date": book["reservation_date"],
        "message": f'Book "{book["title"]}" reserved successfully.'
    })


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("user_id")
    book = Database().return_book(book_id)
    if not user_id:
        raise BadRequest("Missing user_id in header")
    if not book:
        raise NotFound("Book not found")
    if not book["is_reserved"]:
        raise BadRequest("Book is not reserved")
    if book["reserved_by"] != user_id:
        raise Forbidden("You can only cancel your own reservations")

    book["is_reserved"] = False
    book["reserved_by"] = None
    book.pop("reservation_date", None)
    Database().save()

    return jsonify({"message": "Reservation cancelled successfully"})

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    requester_id = request.headers.get("user_id")
    user = Database().return_user(user_id)

    if not requester_id:
        raise BadRequest("Missing user_id in header")
    if requester_id != user_id:
        raise Forbidden("You can only view your own reservations")
    if not user:
        raise NotFound("User not found")

    reserved_books = [
        book for book in db.return_books()
        if book.get("is_reserved") and book.get("reserved_by") == user_id
    ]

    return jsonify(reserved_books)
