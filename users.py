from flask import jsonify, request
from app.application import app
import json

DB_FILE = "db.json"


@app.route("/api/v1/users")
def get_users():
    with open(DB_FILE, "r") as f:
        data = json.load(f)
    return jsonify({"users": data["users"]})

@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    with open(DB_FILE, "r") as f:
        data = json.load(f)

    for user in data["users"]:
        if user["id"] == user_id:
            return jsonify({"user": user})

    return jsonify({"error": "User not found"}), 404


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    user_data = request.get_json()

    if "id" not in user_data or "name" not in user_data:
        return jsonify({"error": "Invalid user data"}), 400

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    for user in data["users"]:
        if user["id"] == user_data["id"]:
            return jsonify({"error": "User already exists"}), 400

    user_data["reserved_books"] = []
    data["users"].append(user_data)

    with open(DB_FILE, "w") as f:
        json.dump(data, f)

    return jsonify({"user": user_data}), 201

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    user_data = request.get_json()

    with open(DB_FILE, "r") as f:
        data = json.load(f)

    for user in data["users"]:
        if user["id"] == user_id:
            if "name" in user_data:
                user["name"] = user_data["name"]
            with open(DB_FILE, "w") as f:
                json.dump(data, f)
            return jsonify({"user": user})

    return jsonify({"error": "User not found"}), 404