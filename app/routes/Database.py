from flask import abort
import json

class Database:
    def __init__(self):
        self.path = "db.json"
        self.open()

    def open(self):
        with open(self.path, 'r') as file:
            self.data = json.load(file)

    def save(self):
        with open(self.path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def get_all_users(self):
        self.open()
        return self.data.get("users", [])

    def create_user(self, user_dict):
        self.open()
        if any(u["username"] == user_dict["username"] for u in self.data["users"]):
            return False
        self.data.setdefault("users", []).append(user_dict)
        self.save()
        return True

    def update_user(self, index, key, value):
        self.open()
        self.data["users"][index][key] = value
        self.save()

    def get_all_books(self):
        self.open()
        return self.data.get("books", [])

    def create_book(self, book_dict):
        self.open()
        self.data.setdefault("books", []).append(book_dict)
        self.save()

    def delete_book(self, index):
        self.open()
        try:
            del self.data["books"][index]
            self.save()
        except IndexError:
            abort(404, "Invalid book index")

    def reserve_book(self, book_index, user_index):
        self.open()
        books = self.data["books"]
        users = self.data["users"]

        if books[book_index].get("is_reserved"):
            abort(400, "Book is already reserved")

        books[book_index]["is_reserved"] = True
        books[book_index]["reserved_by"] = users[user_index]["id"]
        users[user_index].setdefault("reserved_books", []).append(books[book_index])
        self.save()

    def cancel_reservation(self, book_index, user_id):
        self.open()
        books = self.data["books"]
        users = self.data["users"]

        book = books[book_index]
        if not book.get("reserved_by"):
            abort(400, "Book is not reserved")

        if book["reserved_by"] != user_id:
            abort(403, "You can only cancel your own reservations")

        for user in users:
            if user["id"] == user_id and "reserved_books" in user:
                user["reserved_books"] = [b for b in user["reserved_books"] if b["id"] != book["id"]]

        book["is_reserved"] = False
        book["reserved_by"] = None
        self.save()

    def get_user_reservations(self, user_index):
        self.open()
        return self.data["users"][user_index].get("reserved_books", [])

db = Database()