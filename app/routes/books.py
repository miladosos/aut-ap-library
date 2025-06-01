from app.application import app
from flask import jsonify , request
import json

@app.route("/api/v1/books")
def get_books():
    with open("db.json") as database:
        data = json.load(database)
    return jsonify(data["books"])


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):

    with open("db.json") as database:
        data = json.load(database)
    for book in data["books"]:
        if (book["id"] == book_id):
            return jsonify(book)

    return jsonify({ f"ketabe {book_id} peyda nashod!"})


@app.route("/api/v1/books", methods=["POST"])
def create_book():
    voroudi = request.get_json()
    if not "title" in voroudi :
        return jsonify({'esm nadare ketabet!'})
    elif not "author" in voroudi:
        return jsonify({'nevisande nadare ketabet!'})
    elif not "isbn" in voroudi:
        return jsonify({'ketabet shenase nadare!'})
    with open("db.json") as f:
        database = json.load(f)

    voroudi["id"] = str(len(database["books"]) + 1)
    voroudi["is_reserved"] = False
    voroudi["reserved_by"] = None

    database["books"].append(voroudi)
    with open("db.json", "w") as f:
        json.dump(database, f)
    return jsonify(voroudi)


@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    with open("db.json") as database:
        data = json.load(database)

    for book in data["books"]:
        if (book["id"] == book_id):
            if (book["is_reserved"]):
                return jsonify({f"in ketab {book_id} reserve shode!"})

            else:
                data["books"].remove(book)

                with open("db.json", "w") as db:
                    json.dump(data, db)

                return jsonify()
        return jsonify({'chenin ketabi nadarim!'})
    return jsonify({"message": "Book deleted"})

