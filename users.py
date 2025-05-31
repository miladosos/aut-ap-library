from flask import jsonify, request
from app.application import app
import json

DB_FILE = "db.json"

def read_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"books": [], "users": []}

def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/v1/users")
def get_users():
    db = read_db()
    users = db.get("users", [])
    return jsonify({"users": users})

@app.route("/api/v1/users/<user_id>")
def get_user(user_id):
    db = read_db()
    users = db.get("users", [])
    for user in users:
        if user["id"] == user_id:
            return jsonify({"user": user})
    return jsonify({"error": "User not found"})

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    db = read_db()
    users = db.get("users", [])
    data = request.get_json()
    new_id = str((max([int(user["id"]) for user in users], default=0) + 1))
    new_user = {
        "id": new_id,
        "username": data.get("username"),
        "name": data.get("name")
    }
    users.append(new_user)
    db["users"] = users
    write_db(db)
    return jsonify({"user": new_user})

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    db = read_db()
    users = db.get("users", [])
    data = request.get_json()
    for user in users:
        if user["id"] == user_id:
            if "username" in data:
                user["username"] = data["username"]
            if "name" in data:
                user["name"] = data["name"]
            db["users"] = users
            write_db(db)
            return jsonify({"user": user})
    return jsonify({"error": "User not found"})
