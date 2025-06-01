from flask import jsonify, request
from app.application import app
from database import get_all_users, get_user_by_id, add_user, update_user

@app.route("/api/v1/users")
def get_users():
    users = get_all_users()
    return jsonify(users), 200

@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    user = get_user_by_id(user_id)
    if user:
        return jsonify(user), 200
    return jsonify({"error": f"User {user_id} not found"}), 404

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    data = request.get_json()
    if not all(key in data for key in ["username", "name", "email"]):
        return jsonify({"error": "Invalid input"}), 400
    try:
        new_user = add_user(data)
        return jsonify(new_user), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user_route(user_id: str):
    data = request.get_json()
    if not all(key in {"username", "name", "email"} for key in data.keys()):
        return jsonify({"error": "Invalid input"}), 400
    updated_user = update_user(user_id, data)
    if updated_user:
        return jsonify(updated_user), 200
    return jsonify({"error": f"User {user_id} not found"}), 404
