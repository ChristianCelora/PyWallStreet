import sys 
import os
import json
import requests
from datetime import datetime, timedelta
from include.strategy import Stock, Strategy

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

def getStockInfo(alpha_key: str, stock: str) -> dict:
    params = {"function": "TIME_SERIES_INTRADAY", "symbol": stock, "interval": "5min", "apikey": alpha_key}
    res = requests.get("https://www.alphavantage.co/query", params=params)
    if res.status_code != 200:
        raise Exception("errore", res.status_code)
    return res.json()

def main():
    stock = "SRPT" #mock
    alpha_key = getAlphaVantageKey()
    res_data = getStockInfo(alpha_key, stock)
    #print(res_data)
    if not "Time Series (5min)" in res_data:
        raise Exception("Errore recupero dati stock ("+stock+")")
    #stoc_index = getStochasticIndex(res_data["Time Series (5min)"])
    strategy = Strategy(stock, res_data["Time Series (5min)"], 14)
    action = strategy.action()
    if action < 0:
        print("Overbought  market. SELL!")
    elif action > 0:
        print("Oversold market. BUY!")
    else:
        print("Wait")

    sys.exit(1)

if __name__ == "__main__":
    main()

