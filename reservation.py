from datetime import datetime

from flask import jsonify, request,Flask
import json
from app.application import app
from flask import j
from flask import Flask,send_from_directory, jsonify, request
import json

app = Flask(__name__)
class Database:
    def __init__(self):
        with open('db.json', 'r') as file:
            self.user = json.load(file)
    def get_user(self):
        return self.user

    def add_changes_user(self):
        with open('db.json', 'w') as file:
            json.dump(self.user, file, indent=4)


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_data = request.get_json()
    user_id = user_data.get("user_id")
    obj = Database()
    all_users = obj.get_user()

    for i in range(len(all_users["books"])):
        if all_users["books"][i]["id"] == book_id:
            if all_users["books"][i]["is_reserved"] == False:
                all_users["books"][i]["is_reserved"] = True

    k = 0
    for i in range(len(all_users["users"])):
        if all_users["users"][i]["id"] == user_id:
            all_users["users"][i]["reserved_books"].append(book_id)
            k = i

    for i in range(len(all_users["books"])):
        if all_users["books"][i]["id"] == book_id:
            all_users["books"][i]["reserved_by"] = user_id
    obj.add_changes_user()

    return jsonify({
        "message": "Book reserved successfully",
        "book_id": book_id,
        "user_id": user_id,
        "reservation_date": datetime.now().isoformat()
    })


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.get_json()
    obj = Database()
    all_users = obj.get_user()

    for i in range(len(all_users["books"])):
        if all_users["books"][i]["id"] == book_id:

            all_users["books"][i]["is_reserved"] = False
            all_users["books"][i]["reserved_by"] = None
    for i in range(len(all_users["users"])):
        if all_users["users"][i]["id"] == user_id:
            all_users["users"][i]["reserved_books"].remove(book_id)

    obj.add_changes_user()
    return jsonify({"message": "Reservation canceled successfully","book_id": book_id,"user_id": user_id})







@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):

    obj = Database()
    all_users = obj.get_user()
    list_book = []
    user_books = []
    user_found = False
    for i in range(len(all_users["users"])):
        if all_users["users"][i]["id"] == user_id:
            list_book = all_users["users"][i]["reserved_books"]
            user_found = True
    if user_found == False:
        return jsonify({"message": "User not found"})
    for i in range(len(all_users["books"])):
        if all_users["books"][i]["id"] in list_book:
            user_books.append(all_users["books"][i])

    """
    Get all reservations for a user

    Args:
        user_id (str): The id of the user

    Returns:
        list: List of reserved books

    Raises:
        BadRequest: If user_id header is missing
        NotFound: If the user is not found
        Forbidden: If requesting user is not the same as target user
    """
    return jsonify(user_books)
