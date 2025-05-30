from flask import request, jsonify
from app.db import load_data, save_data
from app.application import app


@app.route("/api/v1/books", methods=['GET'])
def get_books():
    data = load_data()
    return jsonify(data.get("books", [])), 200


@app.route("/api/v1/books/<book_id>", methods=['POST'])
def create_book():
    data = load_data()
    book = request.get_json()

    if "id" not in book:
        return jsonify({"error": "Book ID is required"}), 400

    data.setdefault("books", []).append(book)
    save_data(data)
    return jsonify(book), 201


@app.route("/api/v1/books", methods=['GET'])
def get_book(book_id):
    data = load_data()
    book = next((b for b in data.get("books", []) if b["id"] == book_id), None)
    if book:
        return jsonify(book), 200
    return jsonify({"error": "Book not found"}), 404


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    data = load_data()
    books = data.get("books", [])
    new_books = [b for b in books if b["id"] != book_id]
    if len(books) == len(new_books):
        return jsonify({"error": "Book not found"}), 404
    data["books"] = new_books
    save_data(data)
    return "", 204
