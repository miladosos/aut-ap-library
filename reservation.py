from datetime import datetime
from flask import jsonify, request
from app.application import app
import json

DB_FILE = "db.json"

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.headers.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id header is required"}), 400

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    user = None
    for u in data["users"]:
        if u["id"] == user_id:
            user = u
            break
    if not user:
        return jsonify({"error": "User not found"}), 404

    for book in data["books"]:
        if book["id"] == book_id:
            if book["is_reserved"]:
                return jsonify({"error": "Book is already reserved"}), 400
            book["is_reserved"] = True
            book["reserved_by"] = user_id
            user["reserved_books"].append(book_id)
            with open(DB_FILE, "w") as f:
                json.dump(data, f)
            return jsonify({
                "book_id": book_id,
                "user_id": user_id,
                "reservation_date": datetime.now().isoformat()
            }), 200

    return jsonify({"error": "Book not found"}), 404


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id header is required"}), 400

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    user = None
    for u in data["users"]:
        if u["id"] == user_id:
            user = u
            break
    if not user:
        return jsonify({"error": "User not found"}), 404

    for book in data["books"]:
        if book["id"] == book_id:
            if book["reserved_by"] != user_id:
                return jsonify({"error": "Book is not reserved by this user"}), 400
            book["is_reserved"] = False
            book["reserved_by"] = None
            if book_id in user["reserved_books"]:
                user["reserved_books"].remove(book_id)
            with open(DB_FILE, "w") as f:
                json.dump(data, f)
            return jsonify({"message": "Reservation cancelled successfully"}), 200

    return jsonify({"error": "Book not found"}), 404


@app.route("/api/v1/users/<user_id>/reservations", methods=["GET"])
def get_user_reservations(user_id: str):
    header_user_id = request.headers.get("user_id")

    if not header_user_id:
        return jsonify({"error": "user_id header is required"}), 400
    if header_user_id != user_id:
        return jsonify({"error": "Access denied"}), 403

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    user = None
    for u in data["users"]:
        if u["id"] == user_id:
            user = u
            break
    if not user:
        return jsonify({"error": "User not found"}), 404

    reserved_books = []
    for book in data["books"]:
        if book["id"] in user["reserved_books"]:
            reserved_books.append(book)

    return jsonify(reserved_books)
