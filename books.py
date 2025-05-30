from app.application import app
from flask import jsonify, request
from database import get_all_books, get_book_by_id, add_book, delete_book

@app.route("/api/v1/books")
def get_books():
    books = get_all_books()
    return jsonify(books), 200

@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    book = get_book_by_id(book_id)
    if book:
        return jsonify(book), 200
    return jsonify({"error": f"Book {book_id} not found"}), 404

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    data = request.get_json()
    if not all(key in data for key in ["title", "author", "isbn"]):
        return jsonify({"error": "Invalid input"}), 400
    try:
        new_book = add_book(data)
        return jsonify(new_book), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book_route(book_id: str):
    success = delete_book(book_id)
    if success:
        return jsonify(), 200
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({"error": f"Book {book_id} not found"}), 404
    return jsonify({"error": f"Book {book_id} is reserved"}), 400