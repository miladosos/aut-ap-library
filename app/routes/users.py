from flask import jsonify
from app.application import app
import json

class Database:
    def __init__(self):
        with open('db.json', 'r') as file:
            self.db = json.load(file)
        self.last_id = max([user["id"] for user in self.db["users"]], default=0)

    def get_db(self):
        return self.db

    def return_books(self):
        return self.db["books"]

    def return_book(self, id):
        return self.db["books"][int(id)]

    def return_users(self):
        return self.db["users"]

    def return_user(self, id):
        for user in self.db["users"]:
            if user["id"] == int(id):
                return user
        return None

    def create_user(self, username, name, email):
        self.last_id += 1
        new_user = {
            "id": self.last_id,
            "username": username,
            "name": name,
            "email": email,
            "reserved_books": []
        }
        self.db["users"].append(new_user)
        with open('db.json', 'w') as file:
            json.dump(self.db, file, indent=4)
        return new_user

    def update_user(self, user_id, username, name, email):
        for user in self.db["users"]:
            if user["id"] == int(user_id):
                user["username"] = username
                user["name"] = name
                user["email"] = email
                break
        with open('db.json', 'w') as file:
            json.dump(self.db, file, indent=4)
        return self.return_user(user_id)

@app.route("/api/v1/users")
def get_users():
    users_info = Database().return_users()
    return jsonify(users_info)

@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    user_info = Database().return_user(user_id)
    if user_info:
        return jsonify(user_info)
    return jsonify({"error": "User not found"}), 404


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    data = request.json
    user = Database().create_user(data["username"], data["name"], data["email"])
    return jsonify(user), 201


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    data = request.json
    updated_user = Database().update_user(user_id, data["username"], data["name"], data["email"])
    return jsonify(updated_user)
