import re
from flask import jsonify, request
from werkzeug.exceptions import NotFound, BadRequest
from app.application import app
from app.routes.data_base import *


@app.route("/api/v1/users")
def get_users():
    users = data_base.data["users"]
    return jsonify(users)


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    users = data_base.data["users"]
    user = [user for user in users if user["id"] == user_id]
    if not user:
        raise NotFound("user not found")
    return jsonify(user[0])


def is_user_exists(user_name, users):
    if not users:
        raise NotFound("No users found")
    for user in users:
        if user_name == user["username"]:
            return True
    return False


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    user = request.get_json()
    user_name = user.get("username", None)
    name = user.get("name", None)
    email = user.get("email", None)
    new_user = {}
    if all([user_name, name, email]):
        if not re.match(r'^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email):
            return jsonify({"invalid": "email"}), 402
        if not re.match(r'^[a-zA-Z0-9_]{3,}$', user_name):
            return jsonify({"invalid": "username"}), 403
        users = data_base.data["users"]
        if not is_user_exists(user_name, users):
            new_user["id"] = "1" if len(users) == 0 else str(int(users[-1]["id"]) + 1)
            new_user["username"] = user_name
            new_user["name"] = name
            new_user["email"] = email
            new_user['reserved_books'] = []
            users.append(new_user)
            data_base.save_data()
            return jsonify(new_user), 201
        raise BadRequest('username already exists')
    raise BadRequest("user is not valid")


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    users = data_base.data["users"]
    for user in users:
        if user["id"] == user_id:
            editing_user = request.get_json()
            user_name = editing_user["username"] if editing_user["username"] else user["username"]
            name = editing_user["name"] if editing_user["name"] else user["name"]
            email = editing_user["email"] if editing_user["email"] else user["email"]
            if not re.match(r'^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email):
                return jsonify({"invalid": "email"}), 402
            if not re.match(r'^[a-zA-Z0-9_]{3,}$', user_name):
                return jsonify({"invalid": "username"}), 403
            if is_user_exists(user_name, users) and user_name != user["username"]:
                raise BadRequest('username already exists')
            user["username"] = user_name
            user["name"] = name
            user["email"] = email
            data_base.save_data()
            return jsonify(user), 201
    raise NotFound("user not found")
