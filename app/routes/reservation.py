from datetime import datetime
from flask import jsonify, request
from app.application import app
import json


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.headers.get("user_id")
    if user_id == None :
        return jsonify({"error": "Invalid input"})
    with open("db.json", "r") as file:
        data = json.load(file)
    for book in data["books"] :
        if book["id"] == book_id :
            for user in data["users"] :
                if user["id"] == user_id :
                    if book["is_reserved"] == True :
                        return jsonify({"error": f"the book with {book_id} is reserved"})
                    else :
                        data["users"].remove(user)
                        data["books"].remove(book)
                        user["reserved_books"].append(book)
                        book["is_reserved"] = True
                        book["reserved_by"] = user
                        data["users"].append(user)
                        data["books"].append(book)
                        with open("db.json", "w") as file:
                            json.dump(data, file)
                        return jsonify(
                            {"book_id": book_id, "user_id": request.headers.get("user_id"),
                            "reservation_date": datetime.now().isoformat()}
                        )
            return jsonify({"error": f"the user with {user_id} id is not found"})
    return jsonify({"error": f"the book with {book_id} id is not found"})

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("user_id")
    if user_id == None :
        return jsonify({"error": "Invalid input"})
    with open("db.json", "r") as file:
        data = json.load(file)
    for book in data["books"] :
        if book["id"] == book_id :
            for user in data["users"] :
                if user["id"] == user_id :
                    if book["is_reserved"] == True :
                        return jsonify({"error": f"the book with {book_id} is reserved"})
                    else :
                        data["users"].remove(user)
                        data["books"].remove(book)
                        user["reserved_books"].remove(book)
                        book["is_reserved"] = False
                        book["reserved_by"] = None
                        data["users"].append(user)
                        data["books"].append(book)
                        with open("db.json", "w") as file:
                            json.dump(data, file)
                        return jsonify({"message": "Reservation cancelled successfully"})
            return jsonify({"error": f"the user with {user_id} id is not found"})
    return jsonify({"error": f"the book with {book_id} id is not found"})

@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    with open("db.json", "r") as file :
        data = json.load(file)
    for user in data["users"] :
        if user["id"] == user_id :
            return jsonify(user["reserved_books"])
    return jsonify({"error": f"the user with {user_id} id is not found"})