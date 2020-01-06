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
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"
    
    mywallet = Wallet(alpaca_key["key"], alpaca_key["secret_key"], None)
    wallStreet = Market(alpha_key, mywallet)

    stock = "LW"
    data = wallStreet.getStockHistory(stock, MIN_INTERVAL)
    strategies = [Strategy(stock, MIN_INTERVAL, MINIUM_PERIODS)]
    test_day = getDay( (list(data[data_key].keys()))[0] )
    print("Day:", test_day)
    print("Starting:", mywallet.getBudget())
    # get only daily data
    daily_data = {}
    for timestamp in data[data_key]:
        if getDay(timestamp) != test_day: # Test only on one day
            continue
        daily_data[timestamp] = data[data_key][timestamp]
    # try strategy
    n_buy = 0
    n_sell = 0
    for timestamp in reversed(list(daily_data.keys())):
        for st in strategies:
            st.addData(timestamp, daily_data[timestamp])
            action = st.action()
            invested = mywallet.getStock(st.name)
            price = float(daily_data[timestamp]["1. open"])
            if action < 0:
                print(timestamp, "Overbought market.")
                if invested > 0:
                    print("SELL!")
                    mywallet.sellStock(st.name, mywallet.getStock(st.name), price)
                    n_sell += 1

            elif action > 0:
                print(timestamp, "Oversold market.")
                if invested == 0:
                    print("BUY!")
                    budget = math.floor(mywallet.getBudget()/len(strategies) * 100) / 100.0
                    mywallet.buyStock(st.name, budget/price, price)
                    n_buy += 1

    #sell everithing left
    for st in strategies:
        mywallet.getStock(st.name)
        wallStreet.sellStock(st.name)
    print("Transactions:", n_buy + n_sell, "BUY:", n_buy, "SELL:", n_sell)
    print("End of the day:", mywallet.getBudget())


if __name__ == "__main__":
    main()