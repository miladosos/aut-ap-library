import json
import os
from flask import jsonify, request
from app.application import app

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "db.json")

def _load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"books": [], "users": []}

def _save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/users")
def get_users():
    data = _load_db()
    return jsonify(data.get("users", []))

@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    data = _load_db()
    user = next((u for u in data.get("users", []) if u["id"] == user_id), None)
    if user:
        return jsonify(user)
    return jsonify({"error": "User not found"}), 404

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    new_user_data = request.get_json()
    if not new_user_data or not all(k in new_user_data for k in ("username", "name", "email")):
        return jsonify({"error": "Missing required fields"}), 400

    data = _load_db()
    users = data.get("users", [])

    # Generate new user ID
    if users:
        new_id = str(max(int(u["id"]) for u in users if u["id"].isdigit()) + 1)
    else:
        new_id = "1"

    # Important: No duplicate username check as per instruction

    new_user = {
        "id": new_id,
        "username": new_user_data["username"],
        "name": new_user_data["name"],
        "email": new_user_data["email"],
        "reserved_books": []
    }
    users.append(new_user)
    data["users"] = users
    _save_db(data)
    return jsonify(new_user), 201

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    update_data = request.get_json()
    if not update_data: # Basic check if body is empty or not JSON
        return jsonify({"error": "Invalid request body"}), 400

    data = _load_db()
    users = data.get("users", [])

    user_idx = next((idx for idx, u in enumerate(users) if u["id"] == user_id), None)

    if user_idx is None:
        return jsonify({"error": "User not found"}), 404

    # Update fields if present in update_data; username is not updated.
    users[user_idx]["name"] = update_data.get("name", users[user_idx]["name"])
    users[user_idx]["email"] = update_data.get("email", users[user_idx]["email"])
    # Do not update users[user_idx]["username"]

    data["users"] = users
    _save_db(data)
    return jsonify(users[user_idx])
