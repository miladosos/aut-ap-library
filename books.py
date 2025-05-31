from app.application import app
from flask import jsonify, request
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

@app.route("/api/v1/books", methods=["GET"])
def get_books():
    books = read_db().get("books", [])
    return jsonify({"books": books})

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    books = read_db().get("books", [])
    for book in books:
        if book["id"] == book_id:
            return jsonify({"book": book})
    return jsonify({"error": "Book not found"})

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    db_data = read_db()
    books = db_data.get("books", [])
    data = request.get_json()
    if not data or "title" not in data or "author" not in data or "isbn" not in data:
        return jsonify({"error": "Invalid request"})
    new_id = str((max([int(book["id"]) for book in books], default=0) + 1))
    new_book = {
        "id": new_id,
        "title": data["title"],
        "author": data["author"],
        "isbn": data["isbn"],
        "is_reserved": False,
        "reserved_by": None
    }
    books.append(new_book)
    db_data["books"] = books
    write_db(db_data)
    return jsonify({"book": new_book})

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    db_data = read_db()
    books = db_data.get("books", [])
    for i, book in enumerate(books):
        if book["id"] == book_id:
            if book.get("is_reserved"):
                return jsonify({"error": "Book is reserved and cannot be deleted"})
            books.pop(i)
            db_data["books"] = books
            write_db(db_data)
            return jsonify({"message": "Book deleted"})
    return jsonify({"error": "Book not found"})
