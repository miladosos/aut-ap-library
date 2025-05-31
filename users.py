from sqlalchemy.dialects.oracle.dictionary import all_users

from app.application import app
from flask import j
from flask import Flask, send_from_directory, jsonify, request
import json
from flask import jsonify
from app.application import app
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


@app.route("/api/v1/users")
def get_users():
    obj = Database()
    all_users = obj.get_user()

    """
    Get all users

    Returns:
        list: List of users
    """
    return jsonify({"users": all_users["users"]})


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    obj = Database()
    all_users = obj.get_user()
    for i in range(len(all_users["users"])):
        if all_users["users"][i]["id"] == user_id:
            return jsonify({"user": all_users["users"][i]})

    """
    Get a user by id

    Args:
        user_id (str): The id of the user

    Returns:
        dict: User details

    Raises:
        NotFound: If the user is not found
    """


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    obj = Database()
    all_users = obj.get_user()
    new_user = request.get_json()
    all_users["users"].append(new_user)
    obj.add_changes_user()
    return jsonify({"user": new_user})



@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    obj = Database()
    all_users = obj.get_user()
    updateee = request.get_json()
    for i in range(len(all_users["users"])):
        if all_users["users"][i]["id"] == user_id:
            all_users["users"][i].update(updateee)
            return jsonify({"user":all_users["users"][i]})
    """
    Update a user by id

    Args:
        user_id (str): The id of the user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
        NotFound: If the user is not found
    """
