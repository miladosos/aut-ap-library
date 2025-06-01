from flask import jsonify, request
from datetime import datetime
import json

from app.application import app

def load_db():
    with open("db.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("db.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/books")
def get_books():
    db = load_db()
    return jsonify({"books": db["books"]})

@app.route("/api/v1/books/<book_id>")
def get_book(book_id):
    db = load_db()
    for book in db["books"]:
        if book["id"] == book_id:
            return jsonify({"book": book})
    return jsonify({"error": "Book not found"}), 404

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    db = load_db()
    data = request.get_json()

    if not data or "title" not in data or "author" not in data or "isbn" not in data:
        return jsonify({"error": "Invalid data"}), 400

    new_id = str(int(db["books"][-1]["id"]) + 1 if db["books"] else 1)
    new_book = {
        "id": new_id,
        "title": data["title"],
        "author": data["author"],
        "isbn": data["isbn"],
        "is_reserved": False,
        "reserved_by": None
    }
    db["books"].append(new_book)
    save_db(db)
    return jsonify({"book": new_book})

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    db = load_db()
    for book in db["books"]:
        if book["id"] == book_id:
            if book["is_reserved"]:
                return jsonify({"error": "Book is reserved"}), 400
            db["books"].remove(book)
            save_db(db)
            return jsonify({"message": "Book deleted"})
    return jsonify({"error": "Book not found"}), 404

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id):
    db = load_db()
    user_id = request.headers.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    book = next((b for b in db["books"] if b["id"] == book_id), None)
    user = next((u for u in db["users"] if u["id"] == user_id), None)

    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    if book["is_reserved"]:
        return jsonify({"error": "Book already reserved"}), 400

    book["is_reserved"] = True
    book["reserved_by"] = user_id
    user["reserved_books"].append(book_id)
    save_db(db)

    return jsonify({
        "book_id": book_id,
        "user_id": user_id,
        "reservation_date": datetime.now().isoformat()
    })

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id):
    db = load_db()
    user_id = request.headers.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    book = next((b for b in db["books"] if b["id"] == book_id), None)
    user = next((u for u in db["users"] if u["id"] == user_id), None)

    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not user:
        return jsonify({"error": "User not found"}), 404
    if not book["is_reserved"] or book["reserved_by"] != user_id:
        return jsonify({"error": "You did not reserve this book"}), 400

    book["is_reserved"] = False
    book["reserved_by"] = None
    user["reserved_books"].remove(book_id)
    save_db(db)

    return jsonify({"message": "Reservation cancelled successfully"})

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id):
    db = load_db()
    header_id = request.headers.get("user_id")

    if not header_id:
        return jsonify({"error": "Missing user_id"}), 400
    if header_id != user_id:
        return jsonify({"error": "Access denied"}), 403

    user = next((u for u in db["users"] if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    reserved_books = [b for b in db["books"] if b["id"] in user["reserved_books"]]
    return jsonify(reserved_books)