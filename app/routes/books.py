from app.application import app
from flask import jsonify
import json

class Database:
    def __init__(self):
        with open('db.json', 'r') as file:
            self.book_info = json.load(file)

    def get_db(self):
        return self.book_info

@app.route("/api/v1/books")
def get_books():

    book_info = Database().get_db()
    return jsonify({"books": book_info["books"]})


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):

    book_info = Database().get_db()["books"]
    for i in book_info:
        if i["id"] == book_id:
            book = i
    if book is None:
        abort(404, description="Book not found")

    return jsonify({"book": book})



@app.route("/api/v1/books", methods=["POST"])
def create_book(id, title, isbn, author):
    book_info = Database().get_db()["books"]
    for i in book_info:
        if i["id"] == id or i["title"] == title or i["isbn"] == isbn or i["author"] == author:
            abort(400, description="Invalid request body")

    new_book = {"author": author,
                "id": id,
                "is_reserved": false,
                "isbn": isbn,
                "reserved_by": null,
                "title": title}

    with open('db.json', 'a') as file:
        json.dump(new_book, file)

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    book_info = Database().get_db()["books"]
    for i, book in book_info:
        if book["id"] == book_id:
            book_info.pop(i)
            with open('db.json', 'w') as file:
                json.dump(Database().get_db(), file, indent=4)
            return jsonify({"message": "Book deleted successfully"})
    return jsonify({"error": "Book not found"}), 404
