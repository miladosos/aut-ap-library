from flask import Blueprint, request, jsonify, abort
import json
import os

books_bp = Blueprint('books', __name__, url_prefix='/api/v1/books')
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'db.json')

def _read_db():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def _write_db(data):
    with open(DB_PATH, 'w') as f:
        json.dump(data, f, indent=4)

@books_bp.route('/', methods=['GET'])
def list_books():

    data = _read_db()
    return jsonify(data.get('books', [])), 200

@books_bp.route('/<int:book_id>', methods=['GET'])
def get_book(book_id):

    data = _read_db()
    for book in data.get('books', []):
        if book.get('id') == book_id:
            return jsonify(book), 200
    abort(404, description="Book not found")

@books_bp.route('/', methods=['POST'])
def create_book():

    payload = request.get_json() or {}
    required_fields = ['title', 'author']
    if not all(field in payload for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    data = _read_db()
    books = data.get('books', [])
    max_id = max((b.get('id', 0) for b in books), default=0)
    new_id = max_id + 1
    new_book = {
        'id': new_id,
        'title': payload['title'],
        'author': payload['author'],
    }
    for k, v in payload.items():
        if k not in new_book:
            new_book[k] = v

    books.append(new_book)
    data['books'] = books
    _write_db(data)
    return jsonify(new_book), 201

@books_bp.route('/<int:book_id>', methods=['PUT'])
def update_book(book_id):

    payload = request.get_json() or {}
    required_fields = ['title', 'author']
    if not all(field in payload for field in required_fields):
        abort(400, description=f"Missing required fields: {required_fields}")

    data = _read_db()
    books = data.get('books', [])
    for idx, book in enumerate(books):
        if book.get('id') == book_id:
            updated_book = {'id': book_id}
            updated_book['title'] = payload['title']
            updated_book['author'] = payload['author']
            for k, v in payload.items():
                if k not in ['id', 'title', 'author']:
                    updated_book[k] = v
            books[idx] = updated_book
            data['books'] = books
            _write_db(data)
            return jsonify(updated_book), 200

    abort(404, description="Book not found")

@books_bp.route('/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):

    data = _read_db()
    books = data.get('books', [])
    reservations = data.get('reservations', [])

    for res in reservations:
        if res.get('book_id') == book_id:
            return jsonify({'error': 'Cannot delete a book that is currently reserved'}), 400

    for idx, book in enumerate(books):
        if book.get('id') == book_id:
            books.pop(idx)
            data['books'] = books
            _write_db(data)
            return '', 204

    abort(404, description="Book not found")
