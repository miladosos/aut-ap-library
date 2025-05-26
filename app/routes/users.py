from flask import jsonify, request, render_template
from werkzeug.exceptions import NotFound,BadRequest

from app.application import app
from .data_base import *
import re
@app.route("/api/v1/users")
def get_users():
    """
    Get all users

    Returns:
        list: List of users
    """
    db = data_base_loder()
    users = db.get('users', None)
    if not users:
        raise NotFound("No users found")
    # return jsonify(users)
    return render_template('all_users.html', users=users)


@app.route("/api/v1/users/<user_id>")
def get_user(user_id: str):
    """
    Get a user by id

    Args:
        user_id (str): The id of the user

    Returns:
        dict: User details

    Raises:
        NotFound: If the user is not found
    """
    db = data_base_loder()
    users = db["users"]
    for user in users:
        if user["id"] == user_id:
            # return jsonify(user)
            return render_template('user.html', user=user)
    raise NotFound("user not found")

def is_user_exists(user_name, db):
    users = db.get('users', None)
    if not users:
        raise NotFound("No users found")
    for user in users:
        if user_name == user["username"]:
            return True
    return False

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """
    user = request.get_json()
    user_name = user.get("username", None)
    name = user.get("name", None)
    email = user.get("email", None)
    new_user = {}
    if all([user_name, name, email]):
        if not re.match(r'^[a-zA-Z0-9._]+@[a-zA-z0-9]+\.[a-zA-Z]{3}$',email):
            raise BadRequest("Invalid email")
        db = data_base_loder()
        if not is_user_exists(user_name, db):
            users_id = db["users_id"]
            for i in range(1, len(users_id)+2):
                i = str(i)
                if i not in users_id:
                    new_user["id"] = i
                    users_id.append(i)
                    db["users_id"] = users_id
                    break
            new_user["username"] = user_name
            new_user["name"] = name
            new_user["email"] = email
            new_user['reserved_books'] = []
            db["users"].append(new_user)
            data_base_dumper(db)
            return jsonify(new_user), 201
            # return render_template('user_management.html', user=new_user)
        raise BadRequest('user already exists')
    raise BadRequest("user is not valid")


@app.route("/api/v1/users/<user_id>", methods=["PUT"])
def update_user(user_id: str):
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
    new_user = request.get_json()

    db = data_base_loder()
    users = db["users"]
    if all([new_user.get("username"), new_user.get("name"), new_user.get("email")]):
        if is_user_exists(new_user.get("username"), db):
            raise BadRequest("username already exists")
        for user in users:
            if user["id"] == user_id:
                user["username"] = new_user["username"]
                user["name"] = new_user["name"]
                user["email"] = new_user["email"]
                db["users"] = users
                data_base_dumper(db)
                return jsonify(user)
                # return render_template('user_management.html', user=new_user)
        raise NotFound("user not found")
    raise BadRequest("user's new information is not valid")


@app.route("/users/manage")
def user_management():
    return render_template("user_management.html")
