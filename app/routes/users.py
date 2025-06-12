from flask import Flask, jsonify, request
import json
from werkzeug.exceptions import NotFound, BadRequest

app = Flask(__name__)
DATA_FILE = 'db.json'

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def find_user(users, user_id):
    for user in users:
        if str(user.get('id')) == str(user_id):
            return user
    return None

@app.route('/api/v1/users', methods=['GET'])
def list_users():
    data = load_data()
    return jsonify(data.get('users', []))

@app.route('/api/v1/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    data = load_data()
    user = find_user(data.get('users', []), user_id)
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/v1/users', methods=['POST'])
def create_user():
    payload = request.get_json()
    if not all(k in payload for k in ('username', 'name', 'email')):
        raise BadRequest("Missing required fields")

    data = load_data()
    users = data.get('users', [])
    new_id = max([user['id'] for user in users], default=0) + 1

    new_user = {
        'id': new_id,
        'username': payload['username'],
        'name': payload['name'],
        'email': payload['email'],
        'reserved_books': []
    }

    users.append(new_user)
    save_data(data)
    return jsonify(new_user), 201

@app.route('/api/v1/users/<string:user_id>', methods=['PUT'])
def update_user(user_id):
    payload = request.get_json()
    if not all(k in payload for k in ('username', 'name', 'email')):
        raise BadRequest("Missing required fields")

    data = load_data()
    user = find_user(data.get('users', []), user_id)
    if not user:
        raise NotFound("User not found")

    user['username'] = payload['username']
    user['name'] = payload['name']
    user['email'] = payload['email']

    save_data(data)
    return jsonify(user)