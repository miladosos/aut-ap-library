from app.application import app
from flask import jsonify
from database import db
from flask import request


@app.route("/api/v1/books")
def get_books():
    books = db.data.get('books', [])
    return jsonify({"books": [books]})


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    books = db.data.get('books')
    for i in books:
        if i.get('id') == book_id:
            return jsonify({"book": i})
    return jsonify({"error": "Book not found"}), 404


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400

    required_fields = {"title", "author", "isbn"}
    if not required_fields.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    books = db.data.get('books', [])
    data["id"] = str(len(books) + 1)
    data["is_reserved"] = False
    data["reserved_by"] = None
    books.append({
        "id": data["id"],
        "title": data["title"],
        "author": data["author"],
        "reserved_by": data["reserved_by"],
        "is_reserved": data["is_reserved"]
    })
    db.save()
    return jsonify({"book": data}), 201


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    
    books = db.data.get('books', [])
    for book in books:
        if book.get('id') == book_id:
            if book.get('reserved', False):
                return jsonify({"error": "Book is reserved"}), 400
            books.remove(book)
            db.data['books'] = books
            db.save()
            break
    else:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"message": "Book deleted"})
