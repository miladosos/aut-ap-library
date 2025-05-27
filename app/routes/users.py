from flask import jsonify, request
from werkzeug.exceptions import NotFound, BadRequest

from app.application import app

import json


with open('db.json', 'r') as file:
    DATABASE = json.load(file)

def commit():
    with open('db.json', 'w') as f:
        json.dump(DATABASE, f)


@app.route("/api/v1/users")
def get_users():
    """
    Get all users

    Returns:
        list: List of users
    """
    return jsonify({"users": DATABASE["users"]})


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    """
    Get a user by id

    Args:
        user_id (str): The id of the user

    Returns:
        dict: User details

    Raises:
        NotFound: If the user is not found
    """

    my_user = None
    for user in DATABASE["users"]:
        if user["id"] == user_id:
            my_user = user

    if my_user is None:
        raise NotFound

    return jsonify({"user": my_user})


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """

    try:
        user = request.get_json()

        user["id"] = str(int(DATABASE["users"][-1]["id"]) + 1)
        user["reserved_books"] = list()
        DATABASE["users"].append(user)
        commit()

        return jsonify({"user": user})
    except BadRequest as e:
        raise BadRequest


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
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
    try:
        details = request.get_json()

        my_user = None
        for user in DATABASE["users"]:
            if user["id"] == user_id:
                my_user = user

        if my_user is None:
            raise NotFound

        my_user["username"] = details["username"]
        my_user["name"] = details["name"]
        my_user["email"] = details["email"]
        commit()

        return jsonify({"user": my_user})
    except BadRequest as e:
        raise BadRequest
