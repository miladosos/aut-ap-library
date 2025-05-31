from flask import jsonify, request, abort
from app.application import app
from app.routes.Database import db

@app.route("/api/v1/users", methods=["GET"])
def get_users():
    return jsonify(db.get_all_users())

@app.route("/api/v1/users/<user_id>", methods=["GET"])
def get_user(user_id):
    for user in db.get_all_users():
        if str(user["id"]) == str(user_id):
            return jsonify(user)
    abort(404, "User not found")

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    data = request.get_json()
    required = ["username", "name", "email"]
    if not all(k in data for k in required):
        abort(400, "Invalid request body")

    data["id"] = str(len(db.get_all_users()) + 1)
    data["reserved_books"] = []
    db.create_user(data)
    return jsonify(data), 201

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    users = db.get_all_users()
    for index, user in enumerate(users):
        if user["id"] == str(user_id):
            data = request.get_json()
            for key, value in data.items():
                if key not in ['id', 'username', 'name', 'email', 'reserved_books']:
                    abort(400, "Invalid field in body")
                db.update_user(index, key, value)
            return jsonify(db.get_all_users()[index])
    abort(404, "User not found")
