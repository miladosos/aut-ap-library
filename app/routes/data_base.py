import json


class DataBase:
    def __init__(self):
        self.data = []
        self.open_data()

    def open_data(self):
        with open('db.json', 'r') as file:
            self.data = json.load(file)

    def save_data(self, data=None):
        if data is None:
            data = self.data
        with open('db.json', 'w') as file:
            json.dump(data, file, indent=4)
        self.open_data()


data_base = DataBase()
