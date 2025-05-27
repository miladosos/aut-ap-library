from werkzeug.exceptions import NotFound, BadRequest

from app.application import app
from flask import jsonify, request
import json

with open('db.json', 'r') as file:
    DATABASE = json.load(file)

def commit():
    with open('db.json', 'w') as f:
        json.dump(DATABASE, f)


@app.route("/api/v1/books")
def get_books():
    """
    Get all books

    Returns:
        list: List of books
    """
    return jsonify({"books": DATABASE["books"]})


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

    for book in DATABASE["books"]:
        if book["id"] == book_id:
            return jsonify({"book": book})
    raise NotFound("Book not found")


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    """
    Create a new book

    Returns:
        dict: Book details

    Raises:
        BadRequest: If the request body is invalid
    """

    try:
        book = request.get_json()
        print(book)

        book["id"] = str(int(DATABASE["books"][-1]["id"]) + 1)
        book["is_reserved"] = False
        book["reserved_by"] = None
        DATABASE["books"].append(book)
        commit()

        return jsonify({"book": book})
    except BadRequest as e:
        raise BadRequest(str(e))


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

    for book in DATABASE["books"]:
        if book["id"] == book_id:
            if book["is_reserved"]:
                raise BadRequest("Book is reserved")

            DATABASE["books"].remove(book)
            commit()
            return jsonify({"message": "Book deleted"})

    raise NotFound("Book not found")
