from importlib.metadata import requires
from pydoc import describe
from flask import jsonify, request
from app.application import app
import json

db_path = "db.json"

#   Helping functions similar to what with used in "book.py":
def read_data_from_db():
    try:
        with open(db_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        if "books" not in data:
            data["books"] = []
        if "users" not in data:
            data["users"] = []
        return data

    except FileNotFoundError:
        print(f"Database file '{db_path}' not found. return empty object.")
        return {"books": [], "users": []}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{db_path}'. return empty object.")
        return {"books": [], "users": []}

def write_data_to_db(data):
    try:
        with open(db_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Could not write to '{db_path}': {e}")

def generate_new_user_id(users_list):
    if not users_list:
        return "1"
    max_id = 0
    for user in users_list:
        user_id_str = user.get("id")
        if isinstance(user_id_str, str) and user_id_str.isdigit():
            user_id_int = int(user_id_str)
            if user_id_int > max_id:
                max_id = user_id_int
    return str(max_id + 1)

@app.route("/api/v1/users", methods=["GET"])
def get_users():
    """
    Get all users

    Returns:
        list: List of users
    """
    db_content = read_data_from_db()
    return jsonify(db_content.get("users", []))

@app.route("/api/v1/users/<user_id>", methods=["GET"])
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
    db_content = read_data_from_db()
    users_list = db_content.get("users", [])
    for user in users_list:
        if user.get("id") == user_id:
            return jsonify(user)
    return jsonify({"error": f"User with id '{user_id}' not found."}), 404

@app.route("/api/v1/users", methods=["POST"])
def create_user():
    """
    Create a new user

    Returns:
        dict: User details

    Raises:
        BadRequest: If the request body is invalid
    """
    if not request.is_json:
        return jsonify({"error": "Invalid request: content-type must be application/json."}), 400

    new_user_data = request.get_json()
    if not isinstance(new_user_data, dict):
        return jsonify({"error": "Invalid request: json object expected."}), 400

    required_fields = ["username", "name", "email"]
    error_messages = []
    for field in required_fields:
        if field not in new_user_data:
            error_messages.append(f"Field '{field}' is missing.")
        elif not new_user_data.get(field):
            error_messages.append(f"Field '{field} cannot be empty.")

    if error_messages:
        return jsonify({"error": "Invalid request: " + "; ".join(error_messages)}), 400

    db_content = read_data_from_db()
    users_list = db_content.get("users", [])

    username_to_check = new_user_data.get("username")
    for user in users_list:
        if user.get("username") == username_to_check:
            return jsonify({"error": f"Username '{username_to_check}' already exists."}), 400

    new_id = generate_new_user_id(users_list)

    created_user = {
        "id": new_id,
        "username": new_user_data["username"],
        "name": new_user_data["name"],
        "email": new_user_data["email"],
        "reserved_books": []
        }

    users_list.append(created_user)
    db_content["users"] = users_list
    write_data_to_db(db_content)

    return jsonify(created_user), 201

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
    if not request.is_json:
        return jsonify({"error": "Invalid request: content-type must be application/json."}), 400

    update_data = request.get_json()
    if not isinstance(update_data, dict):
        return jsonify({"error": "Invalid request: json object expected."}), 400

    if not update_data:
        return jsonify({"error": "Invalid request: no updated data."}), 400

    db_content = read_data_from_db()
    users_list = db_content.get("users", [])

    user_to_update = None
    user_index = -1
    for index, user in enumerate(users_list):
        if user.get("id") == user_id:
            user_to_update = user
            user_index = index
            break

    if user_index == -1:
        return jsonify({"error": f"User with ID '{user_id}' not found."}), 404

    updatable_fields = ["username", "name", "email"]
    updated = False

    for field in updatable_fields:
        if field in update_data:
            new_value = update_data[field]

            if not new_value and field in ["username", "name", "email"]:
                return jsonify({"error": f"Field '{field}; cannot be set to empty."})

            if field == "username" and new_value != user_to_update("username"):
                for other_user in users_list:
                    if other_user.get("username") == new_value and other_user.get("id") != user_id:
                        return jsonify({"error": f"Username '{new_value}' already exist."}), 400

            if user_to_update.get(field) != new_value:
                user_to_update[field] = new_value
                updated = True

    if not updated and update_data:
        valid_field = any(field in update_data for field in updatable_fields)
        if not valid_field:
            return jsonify({"error" : "No valid feild to update data"}), 400

    if updated:
        db_content["users"] = users_list
        write_data_to_db(db_content)

    return jsonify(user_to_update), 200