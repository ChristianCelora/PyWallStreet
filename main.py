import sys 
import os
import json
import requests
import threading, time
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

def getStockInfo(alpha_key: str, stock: str, interval: int) -> dict:
    params = {"function": "TIME_SERIES_INTRADAY", "symbol": stock, "interval": str(interval)+"min", 
        "apikey": alpha_key, "outputsize": "compact"}
    res = requests.get("https://www.alphavantage.co/query", params=params)
    if res.status_code != 200:
        raise Exception("errore", res.status_code)
    return res.json()

def main():
    stock = "SRPT" #mock
    MIN_INTERVAL = 5
    MINIUM_PERIODS = 14
    WAIT_TIME_SECONDS = 60
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"

    alpha_key = getAlphaVantageKey()
    ticker = threading.Event()
    strategy = Strategy(stock, MIN_INTERVAL, MINIUM_PERIODS)
    while not ticker.wait(WAIT_TIME_SECONDS):
        res_data = getStockInfo(alpha_key, stock, MIN_INTERVAL)
        if not data_key in res_data:
            raise Exception("Errore recupero dati stock ("+stock+")")
        strategy.addData(res_data[data_key])
        action = strategy.action()
        print(time.ctime())
        if action < 0:
            print("Overbought  market. SELL!")
        elif action > 0:
            print("Oversold market. BUY!")
        else:
            print("Wait")

    sys.exit(1)

if __name__ == "__main__":
    main()

