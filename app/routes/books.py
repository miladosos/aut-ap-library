from app.application import app
from flask import jsonify, request
import json

@app.route("/api/v1/books")
def get_books():
    
    with open("db.json") as db:
        data = json.load(db)

    return jsonify(data["books"]), 200


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):

    with open("db.json") as db:
        data = json.load(db)

    for book in data["books"]:
        if (book["id"] == book_id):
            return jsonify(book), 200

    return jsonify({"error": f"Book {book_id} not found"}), 404


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    data = request.get_json()

    if (not "title" in data or not "author" in data or not "isbn" in data):
        return jsonify({"error": "Invalid input"}), 400

    with open("db.json") as f:
        db = json.load(f)

    data["id"] = str(len(db["books"]) + 1)

    data["is_reserved"] = False

    data["reserved_by"] = None

    db["books"].append(data)

    with open("db.json", "w") as f:
        json.dump(db, f)

    return jsonify(data), 201


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):

    with open("db.json") as db:
        data = json.load(db)

    for book in data["books"]:
        if (book["id"] == book_id):
            if (book["is_reserved"]):
                return jsonify({"error": f"Book {book_id} is reserved"}), 400

            else:
                data["books"].remove(book)

                with open("db.json", "w") as db:
                    json.dump(data, db)
                
                return jsonify(), 200

    return jsonify({"error": f"Book {book_id} not found"}), 404
