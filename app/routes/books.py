from app.application import app
from flask import jsonify, request, abort
import json

db_path = "db.json"

#helping methods for working with "db.json":
def read_data_from_db():
    try:
        with open(db_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "books" not in data:
                data["books"] = []
            if "users" not in data:
                data["users"] = []
            return data

    except FileNotFoundError:
        print(f"Database file '{db_path}' not found. Returning empty object.")
        return {"books": [], "users": []}

    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{db_path}'. Returning empty object.")
        return {"books": [], "users": []}

#this method writes the data to the db.json file (used in create_book()):
def write_data_to_db(data):
    try:
        with open(db_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Could not write to '{db_path}': {e}")

#this method makes a new id for the next new book (used in create_book()):
def generate_new_book_id(books_list):
    if not books_list:
        return "1"
    max_id = 0
    for book in books_list:
        book_id_str = book.get("id")
        if isinstance(book_id_str, str) and book_id_str.isdigit():
            book_id_int = int(book_id_str)
            if book_id_int > max_id:
                max_id = book_id_int
    return str(max_id + 1)

@app.route("/api/v1/books", methods=["GET"])
def get_books():
    """
    Get all books

    Returns:
        list: List of books
    """
    db_content = read_data_from_db()
    return jsonify(db_content.get("books", []))

@app.route("/api/v1/books/<book_id>", methods=["GET"])
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
    db_content = read_data_from_db()
    books_list = db_content.get("books", [])
    for book in books_list:
        if book.get("id") == book_id:
            return jsonify(book)
    return jsonify({"error": f"Book with the id '{book_id}' not found."}), 404


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    """
    Create a new book

    Returns:
        dict: Book details

    Raises:
        BadRequest: If the request body is invalid
    """
    if not request.is_json:
        abort(400, description="Invalid request: content-type must ne application/json.")

    new_book_data = request.get_json()
    if not isinstance(new_book_data, dict):
        return jsonify({"error", "Invalid request: json object excepted!"}), 400

    required_fields = ["title", "author", "isbn"]
    error_messages = []

    for field in required_fields:
        if field not in new_book_data:
            error_messages.append(f"'{field}' is missing.")
        elif not new_book_data.get(field):
            error_messages.append(f"Filed '{field}' cannot be empty!")

    if error_messages:
        return jsonify({"error": f"Invalid request: " + "; ".join(error_messages)}), 400

    db_content = read_data_from_db()
    books_list = db_content.get("books", [])
    new_id = generate_new_book_id(books_list)

    created_book = {
        "id": new_id,
        "title": new_book_data["title"],
        "author": new_book_data["author"],
        "isbn": new_book_data["isbn"],
        "is_reserved": False,
        "reserved_by": None
    }

    books_list.append(created_book)
    db_content["books"] = books_list
    write_data_to_db(db_content)

    return jsonify(created_book), 201


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
    db_content = read_data_from_db()
    books_list = db_content.get("books", [])
    book_to_delete_index = -1
    found_book = None

    for index, book in enumerate(books_list):
        if book.get("id") == book_id:
            found_book = book
            book_to_delete_index = index
            break

    if not found_book:
        return jsonify({"error": f"Book with ID '{book_id}' not found."}), 404

    if found_book.get("is_reserved", False):
        return jsonify({"error": f"Book with ID '{book_id}' is currently reserved."}), 400

    books_list.pop(book_to_delete_index)
    db_content["books"] = books_list
    write_data_to_db(db_content)
    return jsonify({"message": f"Book with the ID '{book_id}' deleted"}), 200