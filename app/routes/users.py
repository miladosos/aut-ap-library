from flask import jsonify ,request
from app.application import app
from .database import *
from werkzeug.exceptions import NotFound , BadRequest

@app.route("/api/v1/users")
def get_users():
    database = load_data()
    users = database["users"] 
    return jsonify({"users": users})


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    database = load_data()
    users = database["books"]
    for user in users :
      if user["id"] == user_id :
        return jsonify({"user": user})
    raise NotFound("book not found")


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data :
       raise BadRequest("No json body")
    
    required_fields = ["username" , "name" , "email"]
    for fields in required_fields :
       if fields not in data :
          raise BadRequest("Missing fields")
    
    database = load_data()
    users = database["users"]
    
    id = 0
    for _ in users :
       id += 1
       
    new_user = {
        "id" : f"{id}" ,
        "username" : data["username"] , 
        "name" : data["name"] , 
        "email" : data["email"],
        "reserved_books" : [] , 
    }

    return jsonify({"user": new_user})
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    database = load_data()
    users = database["users"]
    data = request.get_json()

    if not data :
       raise BadRequest
    
    for user in users :
        if user_id == user["id"] :
            for key , value in data.items() :
                if key in user :
                    user[key] = value
            return jsonify({"user": user})
    raise NotFound("not found")
    """
    Update a user by id

    Args:
        user_id (str): The id of the user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
        NotFound: If the user is not found
    """
