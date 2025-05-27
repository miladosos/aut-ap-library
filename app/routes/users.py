from flask import jsonify, request
from app.application import app
import json


@app.route("/api/v1/users")
def get_users():
    
    with open("db.json") as db:
        data = json.load(db)

    return jsonify(data["users"]), 200


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):

    with open("db.json") as db:
        data = json.load(db)

    for user in data["users"]:
        if (user["id"] == user_id):
            return jsonify(user), 200

    return jsonify({"error": f"User {user_id} not found"}), 404


@app.route("/api/v1/users", methods=["POST"])
def create_user():
    data = request.get_json()                                               
                                                                           
    if (not "username" in data or not "name" in data or not "email" in data): 
        return jsonify({"error": "Invalid input"}), 400                     
                                                                           
    with open("db.json") as f:                                              
       db = json.load(f)

    for user in db["users"]:
        if (user["username"] == data["username"]):
            return jsonify({"error": "Username already exists"}), 400                     
                                                                           
    data["id"] = str(len(db["users"]) + 1)                                  
                                                                           
    data["reserved_books"] = []                                             
                                                                           
    db["users"].append(data)                                                
                                                                           
    with open("db.json", "w") as f:                                         
       json.dump(db, f)       

    return jsonify(data), 201                                               

@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    data = request.get_json()                                               
    
    for key in data.keys():
        if (not key in {"username", "name", "email"}):
            return jsonify({"error": "Invalid input"}), 400

    with open("db.json") as f:
        db = json.load(f)

    for user in db["users"]:
        if (user["id"] == user_id):

            for key in data.keys():
                user[key] = data[key]

            with open("db.json", "w") as f:                                         
                json.dump(db, f)  
            
            return jsonify(user), 200

    return jsonify({"error": f"User {user_id} not found"}), 404
