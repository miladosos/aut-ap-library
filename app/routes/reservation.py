from datetime import datetime

from flask import jsonify, request

from app.application import app

import json


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.headers.get("user_id")

    if user_id == None:
        return jsonify({"error": "Invalid input"}), 400

    with open("db.json") as db:
        data = json.load(db)

    user_u = None
    book_u = None

    for book in data["books"]:
        if book["id"] == book_id:
            book_u = book

    for user in data["users"]:
        if user["id"] == user_id:
            user_u = user

    if user_u == None or book_u == None:
        return jsonify({"error": "Book or User not found"}), 404

    if book_u["is_reserved"]:
        return jsonify({"error": "Book already reserved"}), 400

    book_u["is_reserved"] = True
    book_u["reserved_by"] = user_id
    user_u["reserved_books"].append({"book_id": book_id, "user_id": user_id, "reservation_date": datetime.now().isoformat()})

    with open("db.json", "w") as db:
        json.dump(data, db)

    return jsonify(user_u["reserved_books"][-1]), 200


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("user_id")

    with open("db.json") as db:   
        data = json.load(db)

    the_user = None
    the_book = None

    for book in data["books"]:
        if book["id"] == book_id:
            the_book = book        
    
    for user in data["users"]:
        if user["id"] == user_id:
            the_user = user

    if the_user == None or the_book == None:
        return jsonify({"error": "Book or User not found"}), 404

    if the_book["reserved_by"] != user_id:
        return jsonify({"error": "Book already reserved"}), 400

    the_book["is_reserved"] = False
    the_book["reserved_by"] = None
    
    for ans in the_user["reserved_books"]:
        if ans["book_id"] == book_id:
            the_user["reserved_books"].remove(ans)

    with open("db.json", "w") as db:
        json.dump(data, db)

    return jsonify({"message": "Reservation cancelled successfully"}), 200
    


@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):

    with open("db.json") as db:   
        data = json.load(db)

    for user in data["users"]:
        if user["id"] == user_id:
            return jsonify(user["reserved_books"]), 200

    return jsonify({"error": "User not found"}), 404
