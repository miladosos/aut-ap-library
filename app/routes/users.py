from flask import Blueprint, request, jsonify, abort
import json
import os

users_bp = Blueprint('users', __name__, url_prefix='/api/v1/users')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db.json')
def _read_db():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def _write_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@users_bp.route('/', methods=['GET'])
def list_users():

    data = _read_db()
    return jsonify(data.get('users', [])), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):

    data = _read_db()
    for user in data.get('users', []):
        if user.get('id') == user_id:
            return jsonify(user), 200
    abort(404, description="User not found")

@users_bp.route('/', methods=['POST'])
def create_user():

    payload = request.get_json() or {}
    required_fields = ['name', 'email']
    if not all(field in payload for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    data = _read_db()
    users = data.get('users', [])

    max_id = max((u.get('id', 0) for u in users), default=0)
    new_id = max_id + 1
    new_user = {
        'id': new_id,
        'name': payload['name'],
        'email': payload['email'],
    }

    for k, v in payload.items():
        if k not in new_user:
            new_user[k] = v
    users.append(new_user)
    data['users'] = users
    _write_db(data)
    return jsonify(new_user), 201

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):

    payload = request.get_json() or {}
    required_fields = ['name', 'email']
    if not all(field in payload for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    data = _read_db()
    users = data.get('users', [])
    for idx, user in enumerate(users):
        if user.get('id') == user_id:
            updated_user = {'id': user_id}
            updated_user['name'] = payload['name']
            updated_user['email'] = payload['email']
            # copy any extra keys
            for k, v in payload.items():
                if k not in ['id', 'name', 'email']:
                    updated_user[k] = v

            users[idx] = updated_user
            data['users'] = users
            _write_db(data)
            return jsonify(updated_user), 200

    abort(404, description="User not found")

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):

    data = _read_db()
    users = data.get('users', [])
    reservations = data.get('reservations', [])

    for res in reservations:
        if res.get('user_id') == user_id:
            return jsonify({'error': 'Cannot delete a user with active reservations'}), 400

    for idx, user in enumerate(users):
        if user.get('id') == user_id:
            users.pop(idx)
            data['users'] = users
            _write_db(data)
            return '', 204

    abort(404, description="User not found")
