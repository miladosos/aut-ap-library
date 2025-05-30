from app.application import app
from flask import jsonify, request
import json

@app.route("/api/v1/books")
def get_books():
    with open("db.json", 'r') as file :
        data = json.load(file)
    return jsonify(data["books"])

@app.route("/api/v1/books/<book_id>")
def get_book(book_id : str):
    with open("db.json", 'r') as file:
        data = json.load(file)
    for book in data["books"] :
        if book["id"] == book_id :
            return jsonify({"book": book})
        else:
            return jsonify({"error" :f"the book with {book_id} id is not found"})

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    new_book = request.get_json()
    if not "title" in new_book or not "author" in new_book or not "isbn" in new_book :
        return jsonify({"error": "Invalid input"})
    with open("db.json", "r") as file:
        data = json.load(file)
    new_book["id"] = str(len(data["books"]) + 1)
    new_book["is_reserved"] = False
    new_book["reserved_by"] = None
    data["books"].append(new_book)
    with open("db.json", "w") as file:
        json.dump(data, file)
    return jsonify({"book" : new_book})

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    with open("db.json", "r") as file :
        data = json.load(file)
    for book in data["books"] :
     if book["id"] == book_id :
         if book["is_reserved"] == True :
             return jsonify({"error" : f"the book with {book_id} is reserved"})
         data["books"].remove(book)
         with open("db.json", "w") as file:
             json.dump(data, file)
         return jsonify({"message": f"Book with {book_id} deleted successfully"})
    return jsonify({"error" :f"the book with {book_id} id is not found"})
