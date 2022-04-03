import pytest
import os 
import json
from include.logger import Logger

PATH = os.path.join(os.path.dirname(__file__), "generated")
FILENAME = "test_log_file"
@pytest.fixture(scope="module")
def logger():
    clear_previous_test_runs()
    logger = Logger(PATH, FILENAME)
    return logger

def clear_previous_test_runs():
    path = os.path.join(PATH,FILENAME)
    if os.path.exists(path):
        os.remove(path)

def test_log_file_creation(logger):
    assert os.path.exists(logger.path) == True
    assert os.path.isfile(logger.path) == True

def test_log_action(logger):
    obj = {
            "stock": "TEST",
            "action": "buy",
            "qty": 10,
            "price": 9.50,
            "budget": 1400
        }
    logger.log_action(obj["stock"], obj["action"], obj["qty"], obj["price"], obj["budget"]) 
    with open(logger.path, "r") as input_data:
        json_data = json.load(input_data)
    assert json_data == [obj]