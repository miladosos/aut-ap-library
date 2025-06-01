from flask import Blueprint, request, jsonify, abort
import json
import os
from datetime import datetime

reservation_bp = Blueprint('reservations', __name__, url_prefix='/api/v1/reservations')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db.json')

def _read_db():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def _write_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@reservation_bp.route('/', methods=['GET'])
def list_reservations():

    data = _read_db()
    return jsonify(data.get('reservations', [])), 200

@reservation_bp.route('/<int:resv_id>', methods=['GET'])
def get_reservation(resv_id):

    data = _read_db()
    for resv in data.get('reservations', []):
        if resv.get('id') == resv_id:
            return jsonify(resv), 200
    abort(404, description="Reservation not found")

@reservation_bp.route('/', methods=['POST'])
def create_reservation():

    payload = request.get_json() or {}
    required_fields = ['book_id', 'user_id']
    if not all(field in payload for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    data = _read_db()
    books = data.get('books', [])
    users = data.get('users', [])
    reservations = data.get('reservations', [])
    book_id = payload['book_id']
    user_id = payload['user_id']

    if not any(b.get('id') == book_id for b in books):
        abort(404, description="Book not found")

    if not any(u.get('id') == user_id for u in users):
        abort(404, description="User not found")

    for resv in reservations:
        if resv.get('book_id') == book_id:
            return jsonify({'error': 'Book is already reserved'}), 400

    max_id = max((r.get('id', 0) for r in reservations), default=0)
    new_id = max_id + 1
    new_resv = {
        'id': new_id,
        'book_id': book_id,
        'user_id': user_id,
        'reserved_at': datetime.utcnow().isoformat() + 'Z'
    }
    reservations.append(new_resv)
    data['reservations'] = reservations
    _write_db(data)
    return jsonify(new_resv), 201

@reservation_bp.route('/<int:resv_id>', methods=['DELETE'])
def delete_reservation(resv_id):

    data = _read_db()
    reservations = data.get('reservations', [])
    for idx, resv in enumerate(reservations):
        if resv.get('id') == resv_id:
            reservations.pop(idx)
            data['reservations'] = reservations
            _write_db(data)
            return '', 204

    abort(404, description="Reservation not found")
