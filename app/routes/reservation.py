from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound, Forbidden
from datetime import datetime
import json

app = Flask(__name__)
DATA_FILE = 'db.json'

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def find_by_id(items, item_id):
    for item in items:
        if item.get('id') == str(item_id):
            return item
    return None

@app.route('/api/v1/books/<string:book_id>/reserve', methods=['POST'])
def reserve(book_id):
    user_id = request.headers.get('user_id')
    if not user_id:
        raise BadRequest("Missing user_id in request headers.")

    data = load_data()
    user = find_by_id(data.get('users', []), user_id)
    book = find_by_id(data.get('books', []), book_id)

    if not user:
        raise NotFound("User not found.")
    if not book:
        raise NotFound("Book not found.")
    if book.get('is_reserved'):
        raise BadRequest("Book is already reserved.")

    book['is_reserved'] = True
    book['reserved_by'] = user_id
    book['reservation_date'] = datetime.now().isoformat()
    save_data(data)

    return jsonify({
        'book_id': book_id,
        'user_id': user_id,
        'reservation_date': book['reservation_date'],
        'message': f'Book "{book["title"]}" reserved successfully.'
    })

@app.route('/api/v1/books/<string:book_id>/reserve', methods=['DELETE'])
def unreserve(book_id):
    user_id = request.headers.get('user_id')
    if not user_id:
        raise BadRequest("Missing user_id in header")

    data = load_data()
    book = find_by_id(data.get('books', []), book_id)

    if not book:
        raise NotFound("Book not found")
    if not book.get('is_reserved'):
        raise BadRequest("Book is not reserved")
    if book.get('reserved_by') != user_id:
        raise Forbidden("You can only cancel your own reservations")

    book['is_reserved'] = False
    book['reserved_by'] = None
    book.pop('reservation_date', None)
    save_data(data)

    return jsonify({'message': 'Reservation cancelled successfully'})

@app.route('/api/v1/users/<string:user_id>/reservations')
def list_user_reservations(user_id):
    requester = request.headers.get('user_id')
    if not requester:
        raise BadRequest("Missing user_id in header")
    if requester != user_id:
        raise Forbidden("You can only view your own reservations")

    data = load_data()
    user = find_by_id(data.get('users', []), user_id)
    if not user:
        raise NotFound("User not found")

    reservations = [
        b for b in data.get('books', [])
        if b.get('is_reserved') and b.get('reserved_by') == user_id
    ]

    return jsonify(reservations)