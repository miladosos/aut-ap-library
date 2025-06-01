import os
import json
import uuid
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey123'
DB_FILE = 'db.json'

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({'users': [], 'books': []}, f)


def load_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)


def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)



def find_user_by_username(username):
    db = load_db()
    return next((u for u in db['users'] if u['username'] == username), None)


def find_user_by_id(user_id):
    db = load_db()
    return next((u for u in db['users'] if u['id'] == user_id), None)


def find_book_by_id(book_id):
    db = load_db()
    return next((b for b in db['books'] if b['id'] == book_id), None)



def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = find_user_by_id(data['user_id'])
            if not user:
                return jsonify({'error': 'Invalid token'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(user, *args, **kwargs)

    return wrapper



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ('username', 'password', 'name', 'email')):
        return jsonify({'error': 'Missing fields'}), 400
    if find_user_by_username(data['username']):
        return jsonify({'error': 'Username already exists'}), 400

    user = {
        'id': str(uuid.uuid4()),
        'username': data['username'],
        'password': generate_password_hash(data['password']),
        'name': data['name'],
        'email': data['email'],
        'reserved_books': []
    }
    db = load_db()
    db['users'].append(user)
    save_db(db)
    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(k in data for k in ('username', 'password')):
        return jsonify({'error': 'Missing credentials'}), 400
    user = find_user_by_username(data['username'])
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    token = create_token(user['id'])
    return jsonify({'token': token})


@app.route('/books', methods=['GET'])
def get_books():
    db = load_db()
    return jsonify(db['books'])


@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)


@app.route('/books', methods=['POST'])
@token_required
def add_book(user):
    data = request.get_json()
    if not all(k in data for k in ('title', 'author', 'isbn')):
        return jsonify({'error': 'Missing book data'}), 400
    book = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'author': data['author'],
        'isbn': data['isbn'],
        'is_reserved': False,
        'reserved_by': None
    }
    db = load_db()
    db['books'].append(book)
    save_db(db)
    return jsonify(book), 201


@app.route('/books/<book_id>/reserve', methods=['POST'])
@token_required
def reserve_book(user, book_id):
    db = load_db()
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    if book['is_reserved']:
        return jsonify({'error': 'Book already reserved'}), 400
    book['is_reserved'] = True
    book['reserved_by'] = user['id']
    user['reserved_books'].append(book_id)
    # ذخیره دیتابیس
    for i, b in enumerate(db['books']):
        if b['id'] == book_id:
            db['books'][i] = book
    for i, u in enumerate(db['users']):
        if u['id'] == user['id']:
            db['users'][i] = user
    save_db(db)
    return jsonify({'message': 'Book reserved'})


@app.route('/books/<book_id>/cancel', methods=['POST'])
@token_required
def cancel_reservation(user, book_id):
    db = load_db()
    book = find_book_by_id(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    if not book['is_reserved'] or book['reserved_by'] != user['id']:
        return jsonify({'error': 'Not your reservation'}), 403
    book['is_reserved'] = False
    book['reserved_by'] = None
    if book_id in user['reserved_books']:
        user['reserved_books'].remove(book_id)

    for i, b in enumerate(db['books']):
        if b['id'] == book_id:
            db['books'][i] = book
    for i, u in enumerate(db['users']):
        if u['id'] == user['id']:
            db['users'][i] = user
    save_db(db)
    return jsonify({'message': 'Reservation canceled'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
