from flask import jsonify, request
from app.application import app
import json


@app.route("/api/v1/users")
def get_users():
    
    with open("db.json") as db:   
        data = json.load(db)      
                                  
    users = data["users"]         
                                  
    return jsonify(users), 200


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):

    with open("db.json") as db:   
        data = json.load(db)      
                                  
    for user in data["users"]:
        if user["id"] == user_id:
            return jsonify(user), 200
    
    return jsonify({"error": f"user {user_id} not found."}), 404


@app.route("/api/v1/users", methods=["POST"])
def create_user():

    user_result = request.get_json()
    
    if not "username" in user_result or not "name" in user_result or not "email" in user_result:
        return jsonify({"error": "Invalid input."}), 400

    with open("db.json") as db:   
        data = json.load(db)

    new_user = {
      "id": str(int(data["users"][-1]["id"]) + 1),
      "username": user_result["username"],
      "name": user_result["name"],
      "email": user_result["email"],
      "reserved_books": []
    }

    for user in data["users"]:
        if user["username"] == new_user["username"]:
            return jsonify({"error": "Invalid input or duplicate username."}), 400

    data["users"].append(new_user)

    with open("db.json", "w") as db:
        json.dump(data, db)
    
    return jsonify(new_user), 201 


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
    
    user_ch = request.get_json()

    for i in user_ch.keys():
        if not i in {"username", "name", "email"}:
            return jsonify({"error": "Invalid input"}), 400

    with open("db.json") as db:   
        data = json.load(db)

    for user in data["users"]:
        if user["id"] == user_id:
            
            for i in user_ch.keys():
                user[i] = user_ch[i]

            with open("db.json", "w") as db:
                json.dump(data, db)
            return jsonify(user), 200
    
    return jsonify({"error": "User not found."}), 404
