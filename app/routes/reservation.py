from datetime import datetime
from flask import jsonify, request
from app.application import app
import json


@app.route("/api/v1/books/<book_id>/reserve", methods=["POST"])
def reserve_book(book_id: str):
    user_id = request.headers.get("user_id")

    if (user_id == None):
        return jsonify({"peyda nashod!"})
    with open("db.json") as f:
        db = json.load(f)
    u = None
    b = None
    for book in db["books"]:
        if (book["id"] == book_id):
            b = book
    for user in db["users"]:
        if (user["id"] == user_id):
            u = user
    if (u == None or b == None):
        return jsonify({"ketab ya User peyda nashod!"})

    if (b["is_reserved"]):
        return jsonify({"in ketab ghablan reserve shode!"})

    b["is_reserved"] = True
    b["reserved_by"] = user_id
    u["reserved_books"].append({"book_id": book_id, "user_id": user_id, "reservation_date": datetime.now().isoformat()})

    with open("db.json", "w") as f:
        json.dump(db, f)
    return jsonify(u["reserved_books"][-1])


@app.route("/api/v1/books/<book_id>/reserve", methods=["DELETE"])
def cancel_reservation(book_id: str):
    user_id = request.headers.get("user_id")

    with open("db.json") as f:
        db = json.load(f)
    u = None
    b = None
    for book in db["books"]:
        if (book["id"] == book_id):
            b = book
    for user in db["users"]:
        if (user["id"] == user_id):
            u = user
    if (u == None or b == None):
        return jsonify({"ketab ya User peyda nashod!"})
    if (b["reserved_by"] != user_id):
        return jsonify({"ketab ghaablan reserve shode!"})
    b["is_reserved"] = False
    b["reserved_by"] = None
    for res in u["reserved_books"]:
        if res["book_id"] == book_id:
            u["reserved_books"].remove(res)

    with open("db.json", "w") as f:
        json.dump(db, f)
    return jsonify({"Reserve cancell shod! "})


@app.route("/api/v1/users/<user_id>/reservations")
def get_user_reservations(user_id: str):
    with open("db.json") as f:
        db = json.load(f)
    u = None
    for user in db["users"]:
        if (user["id"] == user_id):
            u = user
    if (u == None):
        return jsonify({"User peyda nashod!"})

    return jsonify(u["reserved_books"])
