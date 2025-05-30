import json
from datetime import datetime


def read_db():
    with open("db.json") as f:
        return json.load(f)

def write_db(data) -> None:
    with open("db.json", "w") as f:
        json.dump(data, f, indent=2)

def get_all_books():
    return read_db().get("books", [])

def get_book_by_id(book_id: str):
    books = get_all_books()
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def add_book(book_data):
    db = read_db()
    book_data["id"] = str(len(db["books"]) + 1)
    book_data["is_reserved"] = False
    book_data["reserved_by"] = None
    db["books"].append(book_data)
    write_db(db)
    return book_data

def delete_book(book_id: str) -> bool:
    db = read_db()
    for book in db["books"]:
        if book["id"] == book_id:
            if book["is_reserved"]:
                return False
            db["books"].remove(book)
            write_db(db)
            return True
    return False

def get_all_users():
    return read_db().get("users", [])

def get_user_by_id(user_id: str):
    users = get_all_users()
    for user in users:
        if user["id"] == user_id:
            return user
    return None

def add_user(user_data):
    db = read_db()
    for user in db["users"]:
        if user["username"] == user_data["username"]:
            raise ValueError("Username already exists")
    user_data["id"] = str(len(db["users"]) + 1)
    user_data["reserved_books"] = []
    db["users"].append(user_data)
    write_db(db)
    return user_data

def update_user(user_id: str, user_data):
    db = read_db()
    for user in db["users"]:
        if user["id"] == user_id:
            for key in user_data:
                if key in {"username", "name", "email"}:
                    user[key] = user_data[key]
            write_db(db)
            return user
    return None

def reserve_book(book_id: str, user_id: str):
    db = read_db()
    book = get_book_by_id(book_id)
    user = get_user_by_id(user_id)
    if not book or not user:
        raise ValueError("Book or User not found")
    if book["is_reserved"]:
        raise ValueError("Book already reserved")
    book["is_reserved"] = True
    book["reserved_by"] = user_id
    reservation = {
        "book_id": book_id,
        "user_id": user_id,
        "reservation_date": datetime.now().isoformat()
    }
    user["reserved_books"].append(reservation)
    write_db(db)
    return reservation

def cancel_reservation(book_id: str, user_id: str):
    db = read_db()
    book = get_book_by_id(book_id)
    user = get_user_by_id(user_id)
    if not book or not user:
        raise ValueError("Book or User not found")
    if book["reserved_by"] != user_id:
        raise ValueError("Book not reserved by this user")
    book["is_reserved"] = False
    book["reserved_by"] = None
    for res in user["reserved_books"]:
        if res["book_id"] == book_id:
            user["reserved_books"].remove(res)
            break
    write_db(db)

def get_user_reservations(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")
    return user["reserved_books"]