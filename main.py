from flask import Flask, request, jsonify, abort
import json
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

DB_FILE = 'library_db.json'

class Book:
    def __init__(self, title, author, isbn):
        self.id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.isbn = isbn
        self.is_reserved = False
        self.reserved_by = None

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'is_reserved': self.is_reserved,
            'reserved_by': self.reserved_by
        }

class User:
    def __init__(self, username, password, name, email):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = generate_password_hash(password)
        self.name = name
        self.email = email
        self.reserved_books = []

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'name': self.name,
            'email': self.email,
            'reserved_books': self.reserved_books
        }

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"users": [], "books": []}, f)

def load_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def find_book(book_id):
    db = load_db()
    return next((b for b in db['books'] if b['id'] == book_id), None)

def find_user(user_id):
    db = load_db()
    return next((u for u in db['users'] if u['id'] == user_id), None)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = find_user(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Invalid token'}), 401
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/api/v1/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(key in data for key in ['username', 'password', 'name', 'email']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    db = load_db()
    if any(u['username'] == data['username'] for u in db['users']):
        return jsonify({'error': 'Username exists'}), 400
    
    new_user = User(
        username=data['username'],
        password=data['password'],
        name=data['name'],
        email=data['email']
    )
    
    db['users'].append(new_user.to_dict())
    save_db(db)
    return jsonify({'message': 'User registered'}), 201

@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all(key in data for key in ['username', 'password']):
        return jsonify({'error': 'Missing credentials'}), 400
    
    db = load_db()
    user = next((u for u in db['users'] if u['username'] == data['username']), None)
    
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({'user_id': user['id']}, app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'token': token})

@app.route('/api/v1/books', methods=['GET'])
def get_books():
    return jsonify(load_db()['books'])

@app.route('/api/v1/books/<book_id>', methods=['GET'])
def get_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify(book)

@app.route('/api/v1/books', methods=['POST'])
@token_required
def add_book(current_user):
    data = request.get_json()
    if not all(key in data for key in ['title', 'author', 'isbn']):
        return jsonify({'error': 'Missing book data'}), 400
    
    new_book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn']
    )
    
    db = load_db()
    db['books'].append(new_book.to_dict())
    save_db(db)
    return jsonify(new_book.to_dict()), 201

@app.route('/api/v1/books/<book_id>', methods=['DELETE'])
@token_required
def delete_book(current_user, book_id):
    db = load_db()
    book = find_book(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    if book['is_reserved']:
        return jsonify({'error': 'Book is reserved'}), 400
    
    db['books'] = [b for b in db['books'] if b['id'] != book_id]
    save_db(db)
    return jsonify({'message': 'Book deleted'})

@app.route('/api/v1/books/<book_id>/reserve', methods=['POST'])
@token_required
def reserve_book(current_user, book_id):
    db = load_db()
    book = find_book(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    if book['is_reserved']:
        return jsonify({'error': 'Book already reserved'}), 400
    
    book['is_reserved'] = True
    book['reserved_by'] = current_user['id']
    
    user = find_user(current_user['id'])
    user['reserved_books'].append(book_id)
    
    save_db(db)
    return jsonify({'message': 'Book reserved'})

@app.route('/api/v1/books/<book_id>/cancel', methods=['POST'])
@token_required
def cancel_reservation(current_user, book_id):
    db = load_db()
    book = find_book(book_id)
    
    if not book:
        return jsonify({'error': 'Book not found'}), 404
    if not book['is_reserved']:
        return jsonify({'error': 'Book not reserved'}), 400
    if book['reserved_by'] != current_user['id']:
        return jsonify({'error': 'Not your reservation'}), 403
    
    book['is_reserved'] = False
    book['reserved_by'] = None
    
    user = find_user(current_user['id'])
    user['reserved_books'].remove(book_id)
    
    save_db(db)
    return jsonify({'message': 'Reservation canceled'})

@app.route('/api/v1/users/<user_id>/reservations', methods=['GET'])
@token_required
def get_user_reservations(current_user, user_id):
    if current_user['id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db = load_db()
    user = find_user(user_id)
    reserved_books = [find_book(book_id) for book_id in user['reserved_books']]
    
    return jsonify(reserved_books)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8080)
