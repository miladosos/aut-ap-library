from app.application import app
from flask import jsonify, request
import json

def sync(data_base):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json', 'w') as fp:
        json.dump(data_base, fp)

@app.route("/api/v1/books")
def get_books():
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    return jsonify(data_base['books'])


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    book = {}
    for i in data_base['books']:
        if str(i['id']) == book_id:
            book = i
            break
    return jsonify({"book": book})


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    book = json.loads(request.data.decode())
    print(book)
    book['id'] = str(int(data_base['books'][-1]['id'])+1)
    book['is_reserved'] = False
    book['reserved_by'] = None
    data_base['books'].append(book)
    sync(data_base)
    return jsonify({"book": book})


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    book = {}
    for i in data_base['books']:
        if str(i['id']) == book_id:
            book = i
            break
    del book
    sync(data_base)
    return jsonify({"message": "Book deleted"})
