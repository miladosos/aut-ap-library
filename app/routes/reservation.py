from datetime import datetime
from flask import jsonify, request
from app.application import app
import json

db_path = "db.json"

# Helping methods:
def read_data_from_db():
    try:
        with open (db_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            if "users" not in data:
                data["users"] = []
            if "books" not in data:
                data["books"] = []
            return data
    except FileNotFoundError:
        print(f"Database file '{db_path}' not found. Returning empty object.")
        return {"books": [], "users": []}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from '{db_path}'. Returning empty object.")
        return {"books": [], "users": []}

def write_data_to_db(data):
    try:
        with open(db_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Could not write to '{db_path}': {e}")

@app.route("/api/v1/books/<book_id_param>/reserve", methods=["POST"])
#   [cchanging "book_id" to "book_id_param" for better understanding :")]
def reserve_book(book_id_param: str):
    requesting_user_id = request.headers.get("user_id")
    if not requesting_user_id:
        return jsonify({"error": "user_id header is missing."}), 400

    db_content = read_data_from_db()
    books_list = db_content.get("books", [])
    users_list = db_content.get("users", [])

    book_to_reserve = None
    book_index = -1
    for i, book in enumerate(books_list):
        if book.get("id") == book_id_param:
            book_to_reserve = book
            book_index = i
            break

    if not book_to_reserve:
        return jsonify({"error": f"Book with ID '{book_id_param}' not found."}), 404

    reserving_user = None
    user_index = -1
    for i, user in enumerate(users_list):
        if user.get("id") == requesting_user_id:
            reserving_user = user
            user_index = i
            break

    if not reserving_user:
        return jsonify({"error": f"User with ID '{requesting_user_id}' not found."}), 404

    if book_to_reserve.get("is_reserved", False):
        return jsonify({"error": f"Book with ID '{book_id_param}' is already reserved."}), 400

    db_content["books"][book_index]["is_reserved"] = True
    db_content["books"][book_index]["reserved_by"] = requesting_user_id

    if "reserved_books" not in db_content["users"][user_index] or \
        not isinstance(db_content["users"][user_index].get("reserved_books"), list):
            db_content["users"][user_index]["reserved_books"] = []

    if book_id_param not in db_content["users"][user_index]["reserved_books"]:
        db_content["users"][user_index]["reserved_books"].append(book_id_param)

    write_data_to_db(db_content)
    updated_book_info = db_content["books"][book_index]

    return jsonify({
        "message": "Book was successfully reserved.",
        "book_id": updated_book_info.get("id"),
        "title": updated_book_info.get("title"),
        "is_reserved": updated_book_info.get("is_reserved"),
        "reserved_by": updated_book_info.get("reserved_by"),
        "user_id": updated_book_info.get("reserved_by"),
        "reservation_date": datetime.now().isoformat()
    }), 200

@app.route("/api/v1/books/<book_id_param>/reserve", methods=["DELETE"])
def cancel_reservation(book_id_param: str):
    requesting_user_id = request.headers.get("user_id")
    if not requesting_user_id:
        return jsonify({"error": "user_id header is missing."}), 400

    db_content = read_data_from_db()
    books_list = db_content.get("books", [])

    book_to_cancel = None
    book_index = -1
    for i, book in enumerate(books_list):
        if book.get("id") == book_id_param:
            book_to_cancel = book
            book_index = i
            break

    if not book_to_cancel:
        return jsonify({"error": f"Book with ID '{book_id_param}' not found."}), 404

    if not book_to_cancel.get("is_reserved", False):
        return jsonify({"error": f"Book with ID '{book_id_param}' is not currently reserved."}), 400

    if book_to_cancel.get("reserved_by") != requesting_user_id:
        return jsonify({"error": "Forbidden: You are not allowed to cancel this reservation."}), 403

    original_reserver_id = db_content["books"][book_index]["reserved_by"]
    db_content["books"][book_index]["is_reserved"] = False
    db_content["books"][book_index]["reserved_by"] = None

    original_reserver_index = -1
    for i, user in enumerate(db_content["users"]):
        if user.get("id") == original_reserver_id:
            original_reserver_index = i
            break

    if original_reserver_index != -1 and \
        "reserved_books" in db_content["users"][original_reserver_index] and \
        isinstance(db_content["users"][original_reserver_index].get("reserved_books"), list):
        if book_id_param in db_content["users"][original_reserver_index]["reserved_books"]:
            db_content["users"][original_reserver_index]["reserved_books"].remove(book_id_param)

    write_data_to_db(db_content)

    return jsonify({
        "message": f"Reservation for book ID '{book_id_param}' cancelled successfully."
    }), 200

@app.route("/api/v1/users/<user_id_param_path>/reservations", methods=["GET"])
def get_user_reservations(user_id_param_path: str):
    requesting_user_id_header = request.headers.get("user_id")
    if not requesting_user_id_header:
        return jsonify({"error": "user_id header is missing."}), 400

    if requesting_user_id_header != user_id_param_path:
        return jsonify({"error": "You are not allowed to see other users' reservations."}), 403

    db_content = read_data_from_db()
    users_list = db_content.get("users", [])
    books_list = db_content.get("books", [])

    target_user = None
    for user in users_list:
        if user.get("id") == user_id_param_path:
            target_user = user
            break

    if not target_user:
        return jsonify({"error": f"User with ID '{user_id_param_path}' not found."}), 404

    reserved_books_ids = target_user.get('reserved_books', [])
    reserved_books_details = []

    if reserved_books_ids:
        for book_id_to_find in reserved_books_ids:
            for book in books_list:
                if book.get("id") == book_id_to_find:
                    reservation_data = {
                        "book_id": book.get("id"),
                        "title": book.get("title"),
                        "author": book.get("author"),
                        "isbn": book.get("isbn"),
                        "is_reserved": book.get("is_reserved"),
                        "user_id": book.get("reserved_by")
                    }
                    if book.get("reserved_by") == user_id_param_path:
                        reserved_books_details.append(reservation_data)
                    break
    return jsonify(reserved_books_details), 200