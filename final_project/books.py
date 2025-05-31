from app.application import app
from flask import request, jsonify
from database import db
from werkzeug.exceptions import BadRequest, NotFound


@app.route("/api/v1/books")
def get_books():
    """
    Get all books

    Returns:
        list: List of books
    """
    books = db.get_all_books()
    return jsonify({"books": books})


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
    book = books.get(book_id)

    if book is None:
        raise NotFound(f"{book_id} not found")

    return jsonify({"book": book})


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    """
    Create a new book


    Returns:
        dict: Book details

    Raises:
        BadRequest: If the request body is invalid
    """
    data = request.get_json()

    fields = ["title", "author", "isbn"]
    if not data or not all(field in data for field in fields):
        raise BadRequest("Missing book fields")

    books = db.get_all_books()
    book_id = str(len(books) + 1)

    books[book_id] = {
        "title": data["title"],
        "author": data["author"],
        "isbn": data["isbn"],
        "is_reserved": False,
         "reserved_by": None
    }

    db.save_books(books)
    return jsonify({"book": books[book_id]}), 201


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
    book = books.get(book_id)

    if book is None:
        raise NotFound(f"{book_id} not found")

    if book.get("is_reserved", False):
        raise BadRequest(f"{book_id} is reserved & can not be deleted")

    del books[book_id]
    db.save_books(books)

    return jsonify({"message": "Book deleted"})
