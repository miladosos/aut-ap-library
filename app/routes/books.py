from app.application import app
from flask import jsonify, request
import json

@app.route("/api/v1/books")
def get_books():
                                  
    with open("db.json") as db:   
        data = json.load(db)      
                                  
    books = data["books"]         
                                  
    return jsonify(books), 200


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):

    with open("db.json") as db:   
        data = json.load(db)      
                                  
    for book in data["books"]:
        if book["id"] == book_id:
            return jsonify(book), 200
    
    return jsonify({"error": f"book {book_id} not found."}), 404


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    
    book_result = request.get_json()

    if not "title" in book_result or not "author" in book_result or not "isbn" in book_result:
        return jsonify({"error": "Invalid input."}), 400

    with open("db.json") as db:   
        data = json.load(db)

    new_book = {
      "id": str(int(data["books"][-1]["id"]) + 1),
      "title": book_result["title"],
      "author": book_result["author"],
      "isbn": book_result["isbn"],
      "is_reserved": False,
      "reserved_by": None
    }

    data["books"].append(new_book)

    with open("db.json", "w") as db:
        json.dump(data, db)

    return jsonify(new_book), 201


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):

    with open("db.json") as db:   
        data = json.load(db)

    for i in range(len(data["books"])):
        if book_id == data["books"][i]["id"] and data["books"][i]["is_reserved"] == False:
            
            data["books"].pop(i)

            with open("db.json", "w") as db:
                json.dump(data, db)
            return jsonify(), 200

        elif book_id == data["books"][i]["id"] and data["books"][i]["is_reserved"] == True:
            return jsonify({"error": "Cannot delete book - book is currently reserved."}), 400

    return jsonify({"error": "Book not found."}), 404
