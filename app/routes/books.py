from app.application import app
from flask import jsonify,request
from .database  import *
from werkzeug.exceptions import NotFound , BadRequest

@app.route("/api/v1/books")
def get_books():
    database = load_data()
    books = database["books"] 
    return jsonify({"books": books})


@app.route("/api/v1/books/<book_id>")
def get_book(book_id: str):
    database = load_data()
    books = database["books"]

    for book in books :
      if book["id"] == book_id :
        return jsonify({"book": book})

    raise NotFound("book not found")

@app.route("/api/v1/books", methods=["POST"])
def create_book():
    data = request.get_json()

    if not data :
       raise BadRequest("No json body")
    
    required_fields = ["title" , "author" , "ISBN"]
    for fields in required_fields :
       if fields not in data :
          raise BadRequest("Missing fields")
    database = load_data()
    books = database["books"]
    
    id = 0
    for _ in books :
       id += 1
       
    new_book = {
        "id" : f"{id}" ,
        "title" : data["title"] , 
        "author" : data["author"] , 
        "isbn" : data["isbn"],
        "is_reserved": False ,
        "reserved_by": None , 
    }

    return jsonify({"book": new_book})

    """
    Create a new book

    Returns:
        dict: Book details

    Raises:
        BadRequest: If the request body is invalid
    """

@app.route("/api/v1/books/<book_id>", methods=["DELETE"])
def delete_book(book_id: str):
    database = load_data() 
    books = database["books"]
    for book in books :
       if book_id == book["id"] :
          books.remove(book)
    
    for book in books :
       if book["id"] < book_id :
           book["id"] -= 1

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

