from flask import jsonify, request
from app.application import app
from database import db

@app.route("/api/v1/users")
def get_users():
    
    users = db.data.get('users', [])
    return jsonify({"users": [users]})


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    
    users = db.data.get('users', [])
    for i in users:
        if i.get('id') == user_id:
            return jsonify({"user": i})
    return jsonify({"error": "user not found"}), 404



@app.route("/api/v1/users", methods=["POST"])
def create_user():
    
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400

    required_fields = {"name", "email"}
    if not required_fields.issubset(data.keys()):
        return jsonify({"error": "Missing required fields"}), 400

    users = db.data.get('users', [])
    data["id"] = str(len(users) + 1)

    users.append({
        "id": data["id"],
        "name": data["name"],
        "email": data["email"]
    })
    db.save()
    return jsonify({"user": data}), 201
    


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    
    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid request body"}), 400

    users = db.data.get('users', [])
    user = next((u for u in users if u.get('id') == user_id), None)
    if not user:
        return jsonify({"error": "user not found"}), 404

    for field in ["username","name", "email", "reserved_books"]:
        if field in data:
            user[field] = data[field]

    db.save()
    return jsonify({"user": user})
