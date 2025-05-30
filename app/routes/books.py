import json
import os # Not strictly needed for this version, but good for future DB path handling
from flask import jsonify, request
from app.application import app

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "db.json") # More robust path

def _load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # In a real app, you might initialize db.json here if it's missing
        return {"books": [], "users": []}

def _save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/books")
def get_books():
    data = _load_db()
    return jsonify(data.get("books", []))

@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    data = _load_db()
    book = next((b for b in data.get("books", []) if b["id"] == book_id), None)
    if book:
        return jsonify(book)
    return jsonify({"error": "Book not found"}), 404

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    new_book_data = request.get_json()
    if not new_book_data or not all(k in new_book_data for k in ("title", "author", "isbn")):
        return jsonify({"error": "Missing required fields"}), 400

    data = _load_db()
    books = data.get("books", [])

    # Generate new book ID
    if books:
        new_id = str(max(int(b["id"]) for b in books if b["id"].isdigit()) + 1)
    else:
        new_id = "1"

    new_book = {
        "id": new_id,
        "title": new_book_data["title"], # Fields are validated, can access directly
        "author": new_book_data["author"],
        "isbn": new_book_data["isbn"],
        "is_reserved": False,
        "reserved_by": None
    }
    books.append(new_book)
    data["books"] = books
    _save_db(data)
    return jsonify(new_book), 201

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    data = _load_db()
    books = data.get("books", [])

    book_idx = next((idx for idx, b in enumerate(books) if b["id"] == book_id), None)

    if book_idx is None:
        return jsonify({"error": "Book not found"}), 404

    if books[book_idx].get("is_reserved"):
        return jsonify({"error": "Book is reserved"}), 400

    books.pop(book_idx) # Remove book by index
    data["books"] = books
    _save_db(data)
    return jsonify({"message": "Book deleted"}), 200
