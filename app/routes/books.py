from app.application import app
from flask import jsonify, request, abort
from app.routes.Database import db

@app.errorhandler(400)
def handle_400(e):
    return jsonify(error=str(e)), 400

@app.route("/api/v1/books", methods=["GET"])
def get_books():
    return jsonify(db.get_all_books())

@app.route("/api/v1/books/<book_id>", methods=["GET"])
def get_book(book_id):
    for book in db.get_all_books():
        if book["id"] == str(book_id):
            return jsonify(book)
    abort(404, "Book not found")

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    data = request.get_json()
    required = ["title", "author", "isbn"]
    if not all(k in data for k in required):
        abort(400, "Invalid request body")

    data["id"] = str(len(db.get_all_books()) + 1)
    data["is_reserved"] = False
    data["reserved_by"] = None
    db.create_book(data)
    return jsonify(data), 201

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    books = db.get_all_books()
    for index, book in enumerate(books):
        if book["id"] == str(book_id):
            if book["is_reserved"]:
                abort(400, "Book is reserved")
            db.delete_book(index)
            return jsonify({"book": "Book deleted"})
    abort(404, "Book not found")
