from datetime import datetime
from flask import jsonify, request, abort
from app.application import app
from app.routes.Database import db

@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id):
    user_id = request.headers.get("user_id")
    if not user_id:
        abort(400, "Missing user_id header")

    users = db.get_all_users()
    books = db.get_all_books()

    user_index = next((i for i, u in enumerate(users) if u["id"] == str(user_id)), None)
    book_index = next((i for i, b in enumerate(books) if b["id"] == str(book_id)), None)

    if user_index is None:
        abort(404, "User not found")
    if book_index is None:
        abort(404, "Book not found")

    db.reserve_book(book_index, user_index)

    return jsonify({
        "book_id": str(book_id),
        "user_id": str(user_id),
        "reservation_date": datetime.now().isoformat()
    })

@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id):
    user_id = request.headers.get("user_id")
    if not user_id:
        abort(400, "Missing user_id header")

    books = db.get_all_books()
    for index, book in enumerate(books):
        if book["id"] == str(book_id):
            db.cancel_reservation(index, user_id)
            return jsonify({"message": "Reservation cancelled successfully"})
    abort(404, "Book not found")

@app.route("/api/v1/users/<user_id>/reservations", methods=["GET"])
def get_user_reservations(user_id):
    users = db.get_all_users()
    for i in range(len(users)):
        if str(users[i]["id"]) == str(user_id):
            return jsonify(db.get_user_reservations(i))
    abort(404, "User not found")
