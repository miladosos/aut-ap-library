from datetime import datetime
import json

from flask import jsonify, request, make_response

from app.application import app


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        books = data["books"]
        users = data.get("users", [])
    book = next((book for book in books if book["id"] == book_id), None)
    user_id = input("User ID: ")
    user = next((user for user in users if user["id"] == user_id), None)
    if book is None:
        return jsonify({"error": "BookNotFound"})
    if user is None:
        return jsonify({"error": "UserNotFound"})
    if book["is_reserved"]:
        return jsonify({"error": "BookAlreadyReserved"})
    book["is_reserved"] = True
    book["reserved_by"] = user["id"]
    data["books"] = books
    with open("db.json", "w") as f:
        f.write(json.dumps(data))
    body = {
        "book_id": book_id,
        "user_id": user["id"],
        "reservation_date": datetime.now().isoformat()
    }
    return make_response(jsonify(body), 200)


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        books = data["books"]
        users = data.get("users", [])
    book = next((book for book in books if book["id"] == book_id), None)
    user_id = input("User ID: ")
    user = next((user for user in users if user["id"] == user_id), None)
    if book is None:
        return jsonify({"error": "BookNotFound"})
    if user is None:
        return jsonify({"error": "UserNotFound"})
    if book["is_reserved"] is False:
        return jsonify({"error": "BookNotReserved"})
    book["is_reserved"] = False
    book["reserved_by"] = None
    data["books"] = books
    with open("db.json", "w") as f:
        f.write(json.dumps(data))
    return make_response(jsonify({"message": "Reservation cancelled successfully"}), 200)

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        books = data["books"]
        users = data.get("users", [])
    user = next((user for user in users if user["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "UserNotFound"})
    reservations = [book for book in books if book["reserved_by"] == user_id]
    return make_response(jsonify(reservations), 200)
   