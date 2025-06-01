from app.application import app
from flask import jsonify, request
import json


@app.route("/api/v1/books")
def get_books():
    with open("db.json", "r") as f:
        data = json.load(f)
    return jsonify(data["books"])


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    with open("db.json", "r") as f:
        data = json.load(f)

    for book in data["books"]:
        if book["id"] == book_id:
            return jsonify(book)

    return jsonify({"message": "book not found"})


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    with open("db.json", "r") as f:
        data = json.load(f)

    info = request.get_json()
    book_id = str(len(data["books"]) + 1)
    info["id"] = book_id
    info["is_reserved"] = False
    info["reserved_by"] = None

    if info["title"] and info["author"] and info["isbn"]:
        data["books"].append(info)
        with open("db.json", "w") as f:
            json.dump(data, f)
        return jsonify(info)
    else:
        return jsonify({"message": "enter the information correctly"})


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    with open("db.json", "r") as f:
        data = json.load(f)

    special_book = 0
    for book in data["books"]:
        if book["id"] == book_id:
            special_book = book

    if not special_book:
        return jsonify({"message": "the book not found"})

    if special_book["is_reserved"]:
        return jsonify({"message": "the book is reserved"})

    data["books"].remove(special_book)
    with open("db.json", "w") as f:
        json.dump(data, f)

    return jsonify({"message": "Book deleted"})