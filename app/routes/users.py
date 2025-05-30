from flask import jsonify, request
from app.application import app
import json


@app.route("/api/v1/users")
def get_users():
    with open("db.json", 'r') as file :
        data = json.load(file)
    return jsonify(data["users"])

@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    with open("db.json", 'r') as file:
        data = json.load(file)
    for user in data["users"]:
        if user["id"] == user_id:
            return jsonify({"user": user})
        else:
            return jsonify({"error": f"the user with {user_id} id is not found"})

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    new_user = request.get_json()
    if not "username" in new_user or not "name" in new_user or not "email" in new_user:
        return jsonify({"error": "Invalid input"})
    with open("db.json", "r") as file:
        data = json.load(file)
    new_user["id"] = str(len(data["users"]) + 1)
    new_user["reserved_books"] = []
    data["users"].append(new_user)
    with open("db.json", "w") as file:
        json.dump(data, file)
    return jsonify({"user": new_user})

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str) :
    updated_user = request.get_json()
    if not "username" in updated_user or not "name" in updated_user or not "email" in updated_user:
        return jsonify({"error": "Invalid input"})
    with open("db.json", "r") as file :
        data = json.load(file)
    for user in data["users"] :
        if user["id"] == user_id :
            data["users"].remove(user)
            updated_user["id"] = user_id
            updated_user["reserved_books"] = []
            data["users"].append(updated_user)
            return jsonify ({"user" : updated_user})
    return jsonify({"error": f"the user with {user_id} id is not found"})

