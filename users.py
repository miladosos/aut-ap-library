from flask import jsonify, json, request
from app.application import app


@app.route("/api/v1/users")
def get_users():
    with open("db.json", "r") as f:
        data = json.load(f)
    return jsonify(data["users"])


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    with open("db.json", "r") as f:
        data = json.load(f)

    special_user = 0
    for user in data["users"]:
        if user["id"] == user_id:
            special_user = user

    if not special_user:
        return jsonify({"message": "the user not found"})

    return jsonify(special_user)


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    with open("db.json", "r") as f:
        data = json.load(f)

    info = request.get_json()
    user_id = str(len(data['users']) + 1)
    info["id"] = user_id
    info["reserved_books"] = []
    data["users"].append(info)

    with open("db.json", "w") as f:
        json.dump(data, f)
    return jsonify(info)


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    with open("db.json", "r") as f:
        data = json.load(f)

    special_user = 0
    for user in data["usres"]:
        if user["id"] == user_id:
            special_user = user

    if not special_user:
        return jsonify({"message": "the user not found"})

    info = request.get_json()

    if info["username"] and info["name"] and info["email"]:
        special_user["username"] = info["username"]
        special_user["name"] = info["name"]
        special_user["email"] = info["email"]
        with open("db.json", "w") as f:
            json.dump(data, f)
        return jsonify(special_user)
    else:
        return jsonify({"message": "the information is not correct"})

