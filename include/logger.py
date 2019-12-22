import json
from datetime import datetime, timedelta

class Logger:
    def __init__(self, path):
        today = datetime.today().strftime('%Y_%m_%d')
        self.path = path + "\\" + today + ".json"
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
        with open(self.path, "r") as input_data:
            json_data = json.load(input_data)
        json_data.push(obj)

        with open(self.path, "w") as out_data:
            json.dump(json_data, out_data)
