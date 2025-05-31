from app.application import app
from flask import j
from flask import Flask,send_from_directory, jsonify, request
import json
app = Flask(__name__)
class Database:
    def __init__(self):
        with open('db.json', 'r') as file:
            self.books = json.load(file)
    def get_my_book(self):
        return self.books

    def add_book(self):
        with open('db.json', 'w') as file:
            json.dump(self.books, file, indent=4)
@app.route("/api/v1/books", methods=['GET'])
def get_books():
    book_inf = Database().get_my_book()


    return jsonify({"books": book_inf["books"]})



@app.route("/api/v1/books/<book_id>",methods = ['GET'])
def get_book(book_id: str):
    result = ''
    book_inf = Database().get_my_book()
    for i in book_inf["books"] :
        if i["id"] == book_id :
            return jsonify({"book" : i})

            

    """
    Get a book by id

    Args:
        book_id (str): The id of the book

    Returns:
        dict: Book details

    Raises:
        NotFound: If the book is not found
    """



@app.route("/api/v1/books", methods=["POST"])
def create_book():
    obj = Database()
    book_inf = obj.get_my_book()
    book2 = request.get_json()
    book_inf["books"].append(book2)
    obj.add_book()
    return jsonify({"book": book2})



@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    obj = Database()
    book_inf = obj.get_my_book()
    for i in range(len(book_inf["books"])):
        if book_inf["books"][i]["id"] == book_id:
            del book_inf["books"][i]
            obj.add_book()
            return jsonify({"message": "Book deleted"})


    """
    Delete a book by id

    Args:
        book_id (str): The id of the book

    Returns:
        dict: Success message

    Raises:
        NotFound: If the book is not found
        BadRequest: If the book is reserved
    """

