from flask import request, jsonify
from app.db import load_data, save_data
from app.application import app


@app.route("/api/v1/users", methods=['GET'])
def get_users():
    data = load_data()
    return jsonify(data.get('users', [])), 200


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    data = load_data()
    user = request.get_json()

    if "id" not in user:
        return jsonify({"error": "User ID is required"}), 400

    data.setdefault("users", []).append(user)
    save_data(data)
    return jsonify(user), 201


@app.route("/api/v1/users/<user_id>", methods=['GET'])
def get_user(user_id):
    data = load_data()
    user = next((u for u in data.get('users', []) if u['id'] == user_id), None)
    if user:
        return jsonify(user), 200
    return jsonify({'error': 'User not found'}), 404


@app.route("/api/v1/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    data = load_data()
    users = data.get('users', [])
    new_users = [u for u in users if u['id'] != user_id]
    if len(users) == len(new_users):
        return jsonify({'error': 'User not found'}), 404
    data['users'] = new_users
    save_data(data)
    return '', 204
