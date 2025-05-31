import re

from werkzeug.exceptions import NotFound, BadRequest
from app.application import app
from flask import jsonify, request
from app.routes.data_base import *


@app.route("/api/v1/books")
def get_books():
    books = data_base.data["books"]
    return jsonify(books)


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    books = data_base.data["books"]
    book = [book for book in books if book["id"] == book_id]
    if not book:
        raise NotFound("Book not found")
    return jsonify(book[0])


def is_book_exists(isbn, books):
    if not books:
        raise NotFound('No books found')
    for book in books:
        if book["isbn"] == isbn:
            return True
    return False


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    book = request.get_json()
    title = book.get("title", None)
    author = book.get("author", None)
    isbn = book.get("isbn", None)
    new_book = {}
    if all([title, author, isbn]):
        if not re.match(r'^[0-9-]{13}$', isbn):
            return jsonify({"error": "Invalid ISBN"}), 402
        books = data_base.data["books"]
        if not is_book_exists(isbn, books):
            new_book["id"] = "1" if len(books) == 0 else str(int(books[-1]["id"]) + 1)
            new_book["title"] = title
            new_book["author"] = author
            new_book["isbn"] = isbn
            new_book['is_reserved'] = False
            new_book['reserved_by'] = None
            books.append(new_book)
            data_base.save_data()
            return jsonify(new_book), 201
        raise BadRequest('Book already exists')
    raise BadRequest("Book is not valid")


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    books = data_base.data["books"]
    book = [book for book in books if book["id"] == book_id]
    if not book:
        raise NotFound('Book not found')
    book = book[0]
    if not book['is_reserved']:
        books.remove(book)
        data_base.save_data()
        return jsonify({"message": "Book deleted"})
    raise BadRequest("Book is reserved")
