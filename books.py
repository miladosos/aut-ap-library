import json
from flask import request, jsonify
from app.application import app

@app.route("/api/v1/books", methods=["GET"])
def get_books():
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    return jsonify({"books": data["books"]})

@app.route("/api/v1/books/<book_id>")
def get_book(book_id):
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    for book in data["books"]:
        if book["id"] == book_id:
            return jsonify({"book": book})
    return jsonify({"error": "not found"}), 404

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    book = request.get_json()
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    data["books"].append(book)
    f = open("db.json", "w")
    json.dump(data, f)
    f.close()
    return jsonify({"book": book})

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id):
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    for i in range(len(data["books"])):
        if data["books"][i]["id"] == book_id:
            if "reserved" in data["books"][i] and data["books"][i]["reserved"]:
                return jsonify({"error": "book reserved"}), 400
            data["books"].pop(i)
            f = open("db.json", "w")
            json.dump(data, f)
            f.close()
            return jsonify({"message": "Book deleted"})
    return jsonify({"error": "not found"}), 404
