from app.application import app
from flask import request, jsonify
from database import db
from werkzeug.exceptions import BadRequest, NotFound


@app.route("/api/v1/users")
def get_users():
    """
    Get all users

    Returns:
        list: List of users
    """
    users = db.get_all_users()
    return jsonify({"users": users})


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
    users = db.get_all_users()
    user =  users.get(user_id)

    if user is None:
        raise NotFound(f"{user_id} not found")

    return jsonify({"user": user})


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """
    data = request.get_json()

    fields = ["username", "name", "email"]
    if not data or not all(field in data for field in fields):
        raise BadRequest("Missing user fields")

    users = db.get_all_users()
    user_id = str(len(users) + 1)

    users[user_id] = {
        "username": data["username"],
        "name": data["name"],
        "email": data["email"],
        "reserved_books": []
    }

    db.save_users(users)
    return jsonify({"user": users[user_id]}), 201


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
    data = request.get_json()
    if not data:
        raise BadRequest("the request body is invalid")

    users = db.get_all_users()
    user = users.get(user_id)

    if user is None:
        raise NotFound(f"{user_id} not found")

    for i in ["username", "name", "email"]:
        if i in data:
            user[i] = data[i]

    db.save_users(users)
    return jsonify({"user": user})
