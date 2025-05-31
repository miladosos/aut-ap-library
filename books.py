from app.application import app
from flask import request, jsonify
import json

DB_FILE = "db.json"


@app.route("/api/v1/books", methods=["GET"])
def get_books():
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    return jsonify({"books": data["books"]})

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id: str):
    with open(DB_FILE, "r") as f:
        data = json.load(f)

    for book in data["books"]:
        if book["id"] == book_id:
            return jsonify({"book": book})

    return jsonify({"error": "Book not found"}), 404

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    new_book = request.get_json()

    if "id" not in new_book or "title" not in new_book or "author" not in new_book or "isbn" not in new_book:
        return jsonify({"error": "Missing book fields"}), 400

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    for book in data["books"]:
        if book["id"] == new_book["id"]:
            return jsonify({"error": "Book already exists"}), 400

    new_book["is_reserved"] = False
    new_book["reserved_by"] = None
    data["books"].append(new_book)

    with open(DB_FILE, "w") as f:
        json.dump(data, f)

    return jsonify({"book": new_book}), 201


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    with open(DB_FILE, "r") as f:
        data = json.load(f)

    for book in data["books"]:
        if book["id"] == book_id:
            if book["is_reserved"]:
                return jsonify({"error": "Book is reserved"}), 400
            data["books"].remove(book)
            with open(DB_FILE, "w") as f:
                json.dump(data, f)
            return jsonify({"message": "Book deleted"}), 200

    return jsonify({"error": "Book not found"}), 404