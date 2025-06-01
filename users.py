import json
from flask import request, jsonify
from app.application import app

@app.route("/api/v1/users")
def get_users():
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    return jsonify({"users": data["users"]})

@app.route("/api/v1/users/<user_id>")
def get_user(user_id):
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    for user in data["users"]:
        if user["id"] == user_id:
            return jsonify({"user": user})
    return jsonify({"error": "not found"}), 404

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    user = request.get_json()
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    data["users"].append(user)
    f = open("db.json", "w")
    json.dump(data, f)
    f.close()
    return jsonify({"user": user})

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    update = request.get_json()
    f = open("db.json", "r")
    data = json.load(f)
    f.close()
    for user in data["users"]:
        if user["id"] == user_id:
            for key in update:
                user[key] = update[key]
            f = open("db.json", "w")
            json.dump(data, f)
            f.close()
            return jsonify({"user": user})
    return jsonify({"error": "not found"}), 404
