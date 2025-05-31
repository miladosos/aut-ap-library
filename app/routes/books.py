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
    
    books = db.data.get('books', [])
    new_book = request.json
    new_book['id'] = str(len(books)+ 1)
    print(new_book)
    if new_book and not new_book in books:
        books.append(new_book)
        db.data['books'] = books
        db.save()
        return jsonify(new_book), 201
    return jsonify({"error": "Bad Request"}), 400


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
