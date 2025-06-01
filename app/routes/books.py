from flask import jsonify, request, abort
from app.application import app
from app.data_access import (
    get_all_books, get_book_by_id, add_book,
    update_book, delete_book, search_books
)

@app.route("/api/v1/books", methods=["GET"])
def get_books():
    books = get_all_books()
    return jsonify({"books": books})

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id: str):
    book = get_book_by_id(book_id)
    if not book:
        abort(404, description="Book not found")
    return jsonify({"book": book})

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    payload = request.get_json()
    title = payload.get("title")
    author = payload.get("author")
    isbn = payload.get("isbn")
    if not (title and author and isbn):
        abort(400, description="Missing fields")
    book_data = {"title": title, "author": author, "isbn": isbn}
    new_book = add_book(book_data)
    return jsonify({"book": new_book}), 201

@app.route("/api/v1/books/<book_id>", methods=["PUT"])
def update_book_route(book_id: str):
    payload = request.get_json()
    if not payload:
        abort(400, description="No update data provided")
    updated = update_book(book_id, payload)
    if not updated:
        abort(404, description="Book not found")
    return jsonify({"book": updated})

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book_route(book_id: str):
    success, reason = delete_book(book_id)
    if not success:
        if reason == 'not_found':
            abort(404, description="Book not found")
        if reason == 'reserved':
            abort(400, description="Book is reserved")
    return jsonify({"message": "Book deleted"})

@app.route("/api/v1/books/search", methods=["GET"])
def search_books_route():
    query = request.args.get('query', '')
    if not query:
        abort(400, description="Query parameter is required")
    results = search_books(query)
    return jsonify({"books": results})
