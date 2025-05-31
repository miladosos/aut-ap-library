from datetime import datetime
from flask import jsonify, request
from app.application import app
import json

def sync(data_base):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json', 'w') as fp:
        json.dump(data_base, fp)

@app.route("/api/v1/books/<book_id>/<user_id>/reserve", methods=["POST"])
def reserve_book(book_id: str, user_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    book = {}
    user = {}
    for i in data_base['books']:
        if str(i['id']) == book_id:
            book = i
            break
    for i in data_base['users']:
        if str(i['id']) == user_id:
            user = i
            break
    user['reserved_books'].append(book["id"])
    book['is_reserved'] = True
    book['reserved_by'] = user["id"]
    sync(data_base)
    return jsonify(
        {"book_id": book_id, "user_id": request.headers.get("user_id"), "reservation_date": datetime.now().isoformat()}
    )


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    book = {}
    for i in data_base['books']:
        if str(i['id']) == book_id:
            book = i
            break
    book['is_reserved'] = False
    user_id = str(book['reserved_by'])
    book['reserved_by'] = None
    user = {}
    for i in data_base['users']:
        if str(i['id']) == user_id:
            user = i
            break
    for i in range(len(user['reserved_books'])):
        if str(user['reserved_books'][i]) == str(book['id']):
            del user['reserved_books'][i]
            break
    sync(data_base)
    return jsonify({"message": "Reservation cancelled successfully"})


@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    with open('/home/arian/main/code/chert-pert/aut-ap-library/db.json') as fp:
        data_base = json.load(fp)
    user = {}
    for i in data_base['users']:
        if str(i['id']) == user_id:
            user = i
            break
    book_ids = user['reserved_books']
    books = []
    for book_id in book_ids:
        book = {}
        for i in data_base['books']:
            if str(i['id']) == book_id:
                book = i
                break
        books.append(book)
    return jsonify(books)
