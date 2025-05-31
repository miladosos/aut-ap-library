import json

class Database:
    def __init__(self):
        with open("db.json", "r") as f:
            self.data = json.load(f)

    def get_all_books(self):
        return self.data.get("books", {})

    def get_all_users(self):
        return self.data.get("users", {})

    def save_books(self, books):
        self.data["books"] = books
        with open("db.json", "w") as f:
            json.dump(self.data, f, indent=2)

    def save_users(self, users):
        self.data["users"] = users
        with open("db.json", "w") as f:
            json.dump(self.data, f, indent=2)

db = Database()
