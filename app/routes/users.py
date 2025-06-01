import json
from flask import jsonify, make_response
from app.application import app


@app.route("/api/v1/users")
def get_users():
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        users = data.get("users", [])
    return make_response(jsonify(users), 200)




@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        users = data.get("users", [])
    user = next((user for user in users if user["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "UserNotFound"})
    return make_response(jsonify(user), 200)


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        users = data.get("users", [])
    user = {
        "id": str(len(users) + 1),
        "username": input("Username: "),
        "name": input("Name: "),
        "email": input("Email: "),
        "reserved_books": []
    }
    users.append(user)
    data["users"] = users
    with open("db.json", "w") as f:
        f.write(json.dumps(data))
    return make_response(jsonify(user), 201)


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    with open("db.json", "r") as f:
        data = json.loads(f.read())
        users = data.get("users", [])
    user = next((user for user in users if user["id"] == user_id), None)
    if user is None:
        return jsonify({"error": "UserNotFound"})
    user["username"] = input("Username: ")
    user["name"] = input("Name: ")
    user["email"] = input("Email: ")
    data["users"] = users
    with open("db.json", "w") as f:
        f.write(json.dumps(data))
    return make_response(jsonify(user), 200)
    