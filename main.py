import sys 
import os
import json
import requests

def getAlphaVantageKey() -> str:
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    json_data = ""
    #read file
    with open(script_dir+"\\alpha_vantage_key.json", "r") as f:
        json_data = json.load(f)
    #get JSON data
    if not "key" in json_data:
        raise Exception("chiave AlphaVantage non trovata")
    #get key
    alpha_key = json_data["key"]

    return alpha_key

def getStockInfo(key: str, stock: str):
    params = {"function": "TIME_SERIES_INTRADAY", "symbol": stock, "interval": "5min", "apikey": alpha_key}
    res = requests.get("https://www.alphavantage.co/query", params=params)
    if res.status_code != 200:
        raise Exception("errore", res.status_code)
    return res.json()


def main():
    stock = "SRPT" #mock
    alpha_key = getAlphaVantageKey()
    res_data = getStockInfo(alpha_key, stock)
    print(res_data)
    sys.exit(1)

if __name__ == "__main__":
    main()

