import os
import json
import math
from datetime import datetime, timedelta
from include.market import Market, Wallet
from include.logger import Logger
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

def getAlpacaKey() -> dict:
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    json_data = ""
    alpaca_key = {}
    #read file
    with open(script_dir+"\\alpaca_api_key.json", "r") as f:
        json_data = json.load(f)
    #get JSON data
    if (not "key" in json_data) or (not "secret_key" in json_data):
        raise Exception("chiave Alpaca non trovata")
    #get key
    alpaca_key["key"] = json_data["key"]
    alpaca_key["secret_key"] = json_data["secret_key"]

    return alpaca_key

def getDay(timestamp: str):
    day = timestamp.split(" ")
    return day[0]

def getTime(timestamp: str):
    time = timestamp.split(" ")
    return time[1]

def main():
    alpha_key = getAlphaVantageKey()
    alpaca_key = getAlpacaKey()
    MIN_INTERVAL = 5
    MINIUM_PERIODS = 10
    
    mywallet = Wallet(alpaca_key["key"], alpaca_key["secret_key"], None)
    wallStreet = Market(alpaca_key["key"], alpaca_key["secret_key"], mywallet)
    stock = "GOOGL"
    strategies = [Strategy(stock, MIN_INTERVAL, MINIUM_PERIODS)]
    # try strategy
    n_buy = 0
    n_sell = 0
    current_time = datetime.now()
    market_end = datetime(current_time.year, current_time.month, current_time.day, 18, 00, 00) # mock
    while current_time < market_end:
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print(timestamp)
        for st in strategies:
            data = wallStreet.getStockData(st.name, current_time.isoformat()) # retrive stock data
            if st.name in data:
                print(data[st.name])
                st.addData(timestamp, data[st.name][0])
                action = st.action()
                invested = mywallet.getStock(st.name)
                if action < 0:
                    print(timestamp, "Overbought market.")
                    if invested > 0:
                        print("SELL!")
                        wallStreet.sellStock(st.name, mywallet.getStock(st.name))
                        n_sell += 1

                elif action > 0:
                    print(timestamp, "Oversold market.")
                    if invested == 0:
                        print("BUY!")
                        budget = math.floor(mywallet.getBudget()/len(strategies) * 100) / 100.0
                        wallStreet.buyStock(st.name, budget)
                        n_buy += 1
        current_time = current_time + timedelta(minutes=5)
    #sell everithing left
    for st in strategies:
        mywallet.getStock(st.name)
        wallStreet.sellStock(st.name)
    print("Transactions:", n_buy + n_sell, "BUY:", n_buy, "SELL:", n_sell)
    print("End of the day:", mywallet.getBudget())


if __name__ == "__main__":
    main()