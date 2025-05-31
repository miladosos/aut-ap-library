from flask import jsonify, request
from app.application import app
from database import database

db = database()


@app.route("/api/v1/users")
def get_users():
    """
    Get all users

    Returns:
        list: List of users
    """
    users = db.get_all_users()  # Assuming get_all_users is implemented in database.py
    return jsonify(users)


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
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """
    new_user = request.json
    if not new_user or "id" not in new_user or "name" not in new_user:
        return jsonify({"error": "Invalid user data"}), 400

    users = db.get_all_users()
    if any(u["id"] == new_user["id"] for u in users):
        return jsonify({"error": "User with this ID already exists"}), 400

    users.append(new_user)
    db.save_users(users)  # Assuming save_users is implemented in database.py
    return jsonify(new_user), 201


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
    updated_user = request.json
    if not updated_user:
        return jsonify({"error": "Invalid user data"}), 400

    users = db.get_all_users()
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.update(updated_user)
    db.save_users(users)  # Assuming save_users is implemented in database.py
    return jsonify(user)
