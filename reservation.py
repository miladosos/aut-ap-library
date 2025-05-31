from datetime import datetime
from flask import jsonify, request
from app.application import app
import json

DB_FILE = "db.json"

def read_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"books": [], "users": []}

def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id):
    db = read_db()
    books = db.get("books", [])
    users = db.get("users", [])
    user_id = request.headers.get("user_id")

    for book in books:
        if book["id"] == book_id:
            if book["is_reserved"]:
                return jsonify({"error": "Book already reserved"})
            for user in users:
                if user["id"] == user_id:
                    book["is_reserved"] = True
                    book["reserved_by"] = user_id
                    book["reservation_date"] = datetime.now().isoformat()
                    write_db(db)
                    return jsonify({
                        "book_id": book_id,
                        "user_id": user_id,
                        "reservation_date": book["reservation_date"]
                    })
            return jsonify({"error": "User not found"})
    return jsonify({"error": "Book not found"})

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id):
    db = read_db()
    books = db.get("books", [])
    user_id = request.headers.get("user_id")

    for book in books:
        if book["id"] == book_id:
            if not book["is_reserved"]:
                return jsonify({"error": "Book is not reserved"})
            if book["reserved_by"] != user_id:
                return jsonify({"error": "You didn't reserve this book"})
            book["is_reserved"] = False
            book["reserved_by"] = None
            if "reservation_date" in book:
                del book["reservation_date"]
            write_db(db)
            return jsonify({"message": "Reservation cancelled successfully"})
    return jsonify({"error": "Book not found"})

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id):
    db = read_db()
    books = db.get("books", [])
    result = []
    for book in books:
        if book.get("is_reserved") and book.get("reserved_by") == user_id:
            result.append(book)
    return jsonify(result)
