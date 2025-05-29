from app.application import app
from flask import jsonify, request
from database import database

db = database()

@app.route("/api/v1/books")
def get_books():
    """
    Get all books
    Returns:
        list: List of books
    """
    books = db.get_all_books()
    return jsonify(books)


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    """
    Get a book by id

    Args:
        book_id (str): The id of the book

    Returns:
        dict: Book details

    Raises:
        NotFound: If the book is not found
    """
    books = db.get_all_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    """
    Create a new book

    Returns:
        dict: Book details

    Raises:
        BadRequest: If the request body is invalid
    """
    new_book = request.json
    if not new_book or "id" not in new_book or "title" not in new_book:
        return jsonify({"error": "Invalid book data"}), 400

    books = db.get_all_books()
    if any(b["id"] == new_book["id"] for b in books):
        return jsonify({"error": "Book with this ID already exists"}), 400

    books.append(new_book)
    db.save_books(books)
    return jsonify(new_book), 201


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    """
    Delete a book by id

    Args:
        book_id (str): The id of the book

    Returns:
        dict: Success message

    Raises:
        NotFound: If the book is not found
        BadRequest: If the book is reserved
    """
    books = db.get_all_books()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    books.remove(book)
    db.save_books(books)
    return jsonify({"message": "Book deleted"})
