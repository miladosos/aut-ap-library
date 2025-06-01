from app.application import app
from flask import jsonify, request
import json

@app.route("/api/v1/books")
def get_books():
    with open("db.json", "r") as f:
        books = json.loads(f.read())["books"]
    return jsonify({"books": books})


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    with open("db.json", "r") as f:
        books = json.loads(f.read())["books"]
    book = next((book for book in books if book["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "Not found"})
    return jsonify({"book": book})


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        books = data["books"]
    book = {
        "id": str(len(books) + 1),
        "title": input("Title: "),
        "author": input("Author: "),
        "isbn": input("ISBN: "),
        "is_reserved": False,
        "reserved_by": None,
    }
    books.append(book)
    with open("db.json", "w") as f:
        f.write(json.dumps(data))
    return jsonify({"book": book})


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        books = data["books"]
    book = next((book for book in books if book["id"] == book_id), None)
    if book is None:
        return jsonify({"error": "NotFound"})
    if book["is_reserved"]:
        return jsonify({"error": "BadRequest"})
    books.remove(book)
    data["books"] = books
    with open("db.json", "w") as f:
        f.write(json.dumps(data))
    return jsonify({"message": "Book deleted"})
    
    