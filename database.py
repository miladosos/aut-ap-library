from json import load, dump
from pprint import pprint
class Database:
    
    def __init__(self):
        with open('db.json', 'r') as f:
            self.data = load(f)

    def save(self):
        with open('db.json', 'w') as f:
            dump(self.data)

db = Database()