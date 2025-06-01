import json
from datetime import datetime
from flask import request, jsonify
from app.application import app

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id):
    user_id = request.headers.get("user_id")
    if user_id is None:
        return jsonify({"error": "missing user_id"}), 400

    f = open("db.json", "r")
    data = json.load(f)
    f.close()

    for book in data["books"]:
        if book["id"] == book_id:
            if "reserved" in book and book["reserved"]:
                return jsonify({"error": "already reserved"}), 400
            book["reserved"] = True
            book["reserved_by"] = user_id
            book["reservation_date"] = datetime.now().isoformat()
            f = open("db.json", "w")
            json.dump(data, f)
            f.close()
            return jsonify({"book_id": book_id, "user_id": user_id, "reservation_date": book["reservation_date"]})

    return jsonify({"error": "book not found"}), 404

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id):
    user_id = request.headers.get("user_id")
    if user_id is None:
        return jsonify({"error": "missing user_id"}), 400

    f = open("db.json", "r")
    data = json.load(f)
    f.close()

    for book in data["books"]:
        if book["id"] == book_id:
            if book.get("reserved_by") != user_id:
                return jsonify({"error": "not your reservation"}), 400
            book["reserved"] = False
            book["reserved_by"] = ""
            book["reservation_date"] = ""
            f = open("db.json", "w")
            json.dump(data, f)
            f.close()
            return jsonify({"message": "Reservation cancelled"})

    return jsonify({"error": "book not found"}), 404

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id):
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    user_books = []
    for book in data["books"]:
        if book.get("reserved_by") == user_id:
            user_books.append(book)
    return jsonify(user_books)
