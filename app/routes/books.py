from werkzeug.exceptions import NotFound, BadRequest

from app.application import app
from flask import jsonify, request, render_template
from .data_base import *


@app.route("/api/v1/books")
def get_books():
    """
    Get all books

    Returns:
        list: List of books
    """
    db = data_base_loder()
    books = db.get("books", None)
    if not books:
        raise NotFound('No books found')
    # return jsonify(books)
    return render_template('all_books.html', books=books)

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
    db = data_base_loder()
    books = db["books"]
    for book in books:
        if book["id"] == book_id:
            # return jsonify(book)
            return render_template('book.html',book=book)
    raise NotFound("Book not found")

def is_book_exists(isbn, db):
    books = db.get("books", None)
    if not books:
        raise NotFound('No books found')
    for book in books:
        if book["isbn"] == isbn:
            return True
    return False


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    """
    Create a new book

    Returns:
        dict: Book details

    Raises:
        BadRequest: If the request body is invalid
    """
    book = request.get_json()
    title = book.get("title", None)
    author = book.get("author", None)
    isbn = book.get("isbn", None)
    new_book = {}
    if all([title, author, isbn]):
        db = data_base_loder()
        if not is_book_exists(isbn, db):
            books_id = db["books_id"]
            for i in range(1, len(books_id) + 2):
                i = str(i)
                if i not in books_id:
                    new_book["id"] = i
                    books_id.append(i)
                    db["books_id"] = books_id
                    break
            new_book["title"] = title
            new_book["author"] = author
            new_book["isbn"] = isbn
            new_book['is_reserved'] = False
            new_book['reserved_by'] = None
            db["books"].append(new_book)
            data_base_dumper(db)
            return jsonify(new_book), 201
        raise BadRequest('Book already exists')
    raise BadRequest("Book is not valid")


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
    db = data_base_loder()
    books = db["books"]
    for i, book in enumerate(books):
        if book["id"] == book_id:
            if book["is_reserved"]:
                raise BadRequest('Book already reserved')
            books.pop(i)
            db["books"] = books
            data_base_dumper(db)
            return jsonify({"message": "Book deleted"})
    raise NotFound("Book not found")

@app.route("/books/manage")
def book_management():
    return render_template("book_management.html")


