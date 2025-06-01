from datetime import datetime

from flask import jsonify, request, json

from app.application import app


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"message": "enter the user id"})

    with open("db.json", "r") as f:
        data = json.load()

    special_user = 0
    for user in data["users"]:
        if user["id"] == user_id:
            special_user = user

    special_book = 0
    for book in data["books"]:
        if book["id"] == book_id:
            special_book = book

    if special_book and special_user:
        if special_book["is_reserved"]:
            return jsonify({"message": "the book is reserved currently"})
        special_user["reserved-books"].append(special_book)
        special_book["is_reserved"] = True
        special_book["reserved_by"] = special_user["id"]
        with open("db.json", "w") as f:
            json.dump(data, f)
    else:
        return jsonify({"message": "the book or user not found"})

    return jsonify(
        {"book_id": book_id, "user_id": request.headers.get("user_id"), "reservation_date": datetime.now().isoformat()}
    )


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("user_id")
    if not user_id:
        return jsonify({"message": "enter the user id"})

    with open("db.json", "r") as f:
        data = json.load()

    special_user = 0
    for user in data["users"]:
        if user["id"] == user_id:
            special_user = user

    special_book = 0
    for book in data["books"]:
        if book["id"] == book_id:
            special_book = book

    if special_book and special_user:
        if not special_book in special_user["reserved_books"]:
            return jsonify({"message": "You don't reserved this book"})
        special_user["reserved_books"].remove(special_book)
        special_book["is_reserved"] = False
        special_book["reserved_by"] = None
        with open("db.json", "w") as f:
            json.dump(data, f)
    else:
        return jsonify({"message": "the book or user not found"})

    return jsonify({"message": "Reservation cancelled successfully"})


@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    with open("db.json", "r") as f:
        data = json.load()

    special_user = 0
    for user in data["users"]:
        if user["id"] == user_id:
            special_user = user

    if not special_user:
        return jsonify({"message": "the user not found"})

    return jsonify({"reserved_books": special_user["reserved_books"]})