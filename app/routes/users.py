from flask import jsonify, request, abort
from app.application import app
from app.data_access import (
    get_all_users, get_user_by_id, add_user,
    update_user, delete_user
)

@app.route("/api/v1/users")
def get_users():
    """
    Get all users

    Returns:
        list: List of users
    """
    users = get_all_users()
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
    user = get_user_by_id(user_id)
    if not user:
        abort(404, description="User not found")
    return jsonify({"user": user})


@app.route("/api/v1/users", methods=["POST"])
def create_user_route():
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """
    payload = request.get_json()
    username = payload.get("username")
    name = payload.get("name")
    email = payload.get("email")
    if not (username and name and email):
        abort(400, description="Missing fields")
    user_data = {"username": username, "name": name, "email": email}
    new_user = add_user(user_data)
    return jsonify({"user": new_user}), 201


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user_route(user_id: str):
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
    payload = request.get_json()
    if not payload:
        abort(400, description="No update data provided")
    updated = update_user(user_id, payload)
    if not updated:
        abort(404, description="User not found")
    return jsonify({"user": updated})



@app.route("/api/v1/users/<user_id>", methods=["DELETE"])
def delete_user_routeت(user_id: str):
    success, reason = delete_user(user_id)
    if not success:
        if reason == 'not_found':
            abort(404, description="User not found")
        if reason == 'has_reservations':
            abort(400, description="User has reserved books")
    return jsonify({"message": "User deleted"})