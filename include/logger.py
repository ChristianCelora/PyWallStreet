import json
from json.decoder import JSONDecodeError
import os
from datetime import datetime, timedelta

class Logger:
    def __init__(self, path, name = ""):
        if name == "":
            name = datetime.today().strftime('%Y_%m_%d')
        self.path = os.path.join(path, name + ".json")
        log_file = open(self.path, "w+")    #create file if not exist
        log_file.close()

    def log_action(self, stock: str, action: str, qty: float, price: float, budget: float):
        obj = {
            "stock": stock,
            "action": action,
            "qty": qty,
            "price": price,
            "budget": budget
        }
        json_data = []
        with open(self.path, "r") as input_data:
            try:
                json_data = json.load(input_data)
            except JSONDecodeError: # error on empty file
                pass
        json_data.append(obj)

        with open(self.path, "w") as out_data:
            json.dump(json_data, out_data)
