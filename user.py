from flask import jsonify, request
import json
from app.application import app

def load_db():
    with open("db.json", "r") as f:
        return json.load(f)

def save_db(data):
    with open("db.json", "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/users")
def get_users():
    db = load_db()
    return jsonify({"users": db["users"]})

@app.route("/api/v1/users/<user_id>")
def get_user(user_id):
    db = load_db()
    user = next((u for u in db["users"] if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user})

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    db = load_db()
    data = request.get_json()
    if not data or "username" not in data or "name" not in data or "email" not in data:
        return jsonify({"error": "Invalid data"}), 400

    new_id = str(int(db["users"][-1]["id"]) + 1 if db["users"] else 1)
    new_user = {
        "id": new_id,
        "username": data["username"],
        "name": data["name"],
        "email": data["email"],
        "reserved_books": []
    }
    db["users"].append(new_user)
    save_db(db)
    return jsonify({"user": new_user})

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    db = load_db()
    user = next((u for u in db["users"] if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    
    for field in ["username", "name", "email"]:
        if field in data:
            user[field] = data[field]

    save_db(db)
    return jsonify({"user": user})