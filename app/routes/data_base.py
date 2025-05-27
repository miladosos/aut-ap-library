import json

def data_base_loder():
    with open('db.json', 'r') as f:
        return json.load(f)

def data_base_dumper(db):
    with open('db.json', 'w') as f :
        db["users_id"].sort()
        db["books_id"].sort()
        db["reservations_id"].sort()
        db["users"] = sorted(db["users"], key=lambda  x:x["id"])
        db["books"] = sorted(db["books"], key=lambda  x:x["id"])
        db["reservations"] = sorted(db["reservations"], key=lambda  x:x["id"])
        json.dump(db, f,indent=4)

