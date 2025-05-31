import json
def load_data():
    with open("db.json" , "r") as f:
        return json.load(f)
def save_data(data):
    with open("db.json" , "w") as f :
        json.dump(data , f ,indent=4)