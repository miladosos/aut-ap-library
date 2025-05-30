import json
import os
from datetime import datetime, timezone
from flask import jsonify, request
from app.application import app

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "db.json")

def _load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"books": [], "users": []}

def _save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id_header = request.headers.get("user_id")
    if not user_id_header:
        return jsonify({"error": "user_id header missing"}), 400

    data = _load_db()
    books = data.get("books", [])
    users = data.get("users", [])

    book_idx = next((idx for idx, b in enumerate(books) if b["id"] == book_id), None)
    user_idx = next((idx for idx, u in enumerate(users) if u["id"] == user_id_header), None)

    if book_idx is None or user_idx is None:
        # Original tests more specifically check for book not found then user not found if book exists.
        # This general message might need refinement if specific tests fail on it.
        # For now, aiming for general "Book or user not found"
        if book_idx is None:
             return jsonify({"error": "Book not found"}), 404 # More specific, preferred by some tests
        if user_idx is None:
             return jsonify({"error": "User not found"}), 404 # More specific
        # Fallback, though above should cover
        return jsonify({"error": "Book or user not found"}), 404


    if books[book_idx].get("is_reserved"):
        return jsonify({"error": "Book already reserved"}), 400

    books[book_idx]["is_reserved"] = True
    books[book_idx]["reserved_by"] = user_id_header

    if "reserved_books" not in users[user_idx]:
        users[user_idx]["reserved_books"] = []

    if book_id not in users[user_idx]["reserved_books"]: # Add only if not already there
        users[user_idx]["reserved_books"].append(book_id)

    _save_db(data)

    return jsonify({
        "book_id": book_id,
        "user_id": user_id_header,
        "reservation_date": datetime.now(timezone.utc).isoformat()
    }), 200 # Test test_reserve_book expects 200

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id_header = request.headers.get("user_id")
    if not user_id_header:
        return jsonify({"error": "user_id header missing"}), 400

    data = _load_db()
    books = data.get("books", [])
    users = data.get("users", [])

    book_idx = next((idx for idx, b in enumerate(books) if b["id"] == book_id), None)
    user_idx = next((idx for idx, u in enumerate(users) if u["id"] == user_id_header), None)

    if book_idx is None or user_idx is None:
        if book_idx is None:
             return jsonify({"error": "Book not found"}), 404
        if user_idx is None:
             return jsonify({"error": "User not found"}), 404
        return jsonify({"error": "Book or user not found"}), 404


    if not books[book_idx].get("is_reserved") or books[book_idx].get("reserved_by") != user_id_header:
        return jsonify({"error": "Reservation not found or book not reserved by user"}), 400

    books[book_idx]["is_reserved"] = False
    books[book_idx]["reserved_by"] = None

    if "reserved_books" in users[user_idx] and book_id in users[user_idx]["reserved_books"]:
        users[user_idx]["reserved_books"].remove(book_id)

    _save_db(data)
    return jsonify({"message": "Reservation cancelled"}), 200

@app.route("/api/v1/users/<user_id_path>/reservations")
def get_user_reservations(user_id_path: str):
    data = _load_db()
    users = data.get("users", [])
    all_books = data.get("books", []) # Needed to fetch book details

    target_user = next((u for u in users if u["id"] == user_id_path), None)

    if not target_user:
        return jsonify({"error": "User not found"}), 404

    user_reservation_details = []
    reserved_book_ids = target_user.get("reserved_books", [])

    for r_book_id in reserved_book_ids:
        book_detail = next((b for b in all_books if b["id"] == r_book_id), None)
        if book_detail: # Only include if the reserved book still exists
            user_reservation_details.append({
                "book_id": book_detail["id"], # Original test asserts this key
                "user_id": user_id_path,      # Original test asserts this key
                "title": book_detail.get("title"),
                "author": book_detail.get("author"),
                "isbn": book_detail.get("isbn"),
                "is_reserved": book_detail.get("is_reserved"), # Should be true
                "reserved_by": book_detail.get("reserved_by")  # Should be user_id_path
            })

    return jsonify(user_reservation_details)
