from flask import Flask, jsonify, request, abort
import json
import os

app = Flask(__name__)

DATA_FILE = 'db.json'


def read_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def write_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


@app.route('/api/v1/books', methods=['GET'])
def list_books():
    data = read_data()
    return jsonify({'books': data.get('books', [])})


@app.route('/api/v1/books/<string:book_id>', methods=['GET'])
def get_single_book(book_id):
    books = read_data().get('books', [])
    for book in books:
        if book.get('id') == book_id:
            return jsonify({'book': book})
    abort(404, description='Book not found')


@app.route('/api/v1/books', methods=['POST'])
def add_book():
    new_data = request.get_json()
    required_fields = {'id', 'title', 'isbn', 'author'}

    if not new_data or not required_fields.issubset(new_data.keys()):
        abort(400, description='Missing fields in request')

    books = read_data().get('books', [])
    for b in books:
        if b['id'] == new_data['id'] or b['title'] == new_data['title'] or \
                b['isbn'] == new_data['isbn'] or b['author'] == new_data['author']:
            abort(400, description='Book already exists')

    new_book = {
        'id': new_data['id'],
        'title': new_data['title'],
        'isbn': new_data['isbn'],
        'author': new_data['author'],
        'is_reserved': False,
        'reserved_by': None
    }

    books.append(new_book)
    write_data({'books': books})
    return jsonify({'message': 'Book added'}), 201


@app.route('/api/v1/books/<string:book_id>', methods=['DELETE'])
def remove_book(book_id):
    data = read_data()
    books = data.get('books', [])

    for idx, book in enumerate(books):
        if book.get('id') == book_id:
            books.pop(idx)
            write_data({'books': books})
            return jsonify({'message': 'Book deleted'})

    return jsonify({'error': 'Book not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)