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

def getDay(timestamp: str):
    day = timestamp.split(" ")
    return day[0]

def getTime(timestamp: str):
    time = timestamp.split(" ")
    return time[1]

def main():
    alpha_key = getAlphaVantageKey()
    STARTING_BUDGET = 1000
    MIN_INTERVAL = 5
    MINIUM_PERIODS = 10
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"
    
    mywallet = Wallet(STARTING_BUDGET, None)
    wallStreet = Market(alpha_key, mywallet)
    data = wallStreet.getStockHistory("SPRT", MIN_INTERVAL)
    strategies = [Strategy("SPRT", MIN_INTERVAL, MINIUM_PERIODS)]
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
    for timestamp in reversed(list(daily_data.keys())):
        for st in strategies:
            st.addData(timestamp, daily_data[timestamp])
            action = st.action()
            invested = mywallet.getStock(st.name)
            price = float(daily_data[timestamp]["1. open"])
            if action < 0:
                print(timestamp, "Overbought  market. SELL!")
                if invested > 0:
                    mywallet.sellStock(st.name, mywallet.getStock(st.name), price)

            elif action > 0:
                print(timestamp, "Oversold market. BUY!")
                if invested == 0:
                    budget = math.floor(mywallet.getBudget()/5 * 100) / 100.0
                    mywallet.buyStock(st.name, budget/price, price)

    #sell everithing left
    for st in strategies:
        mywallet.getStock(st.name)
        wallStreet.sellStock(st.name)

    print ("End of the day:", mywallet.getBudget())


if __name__ == "__main__":
    main()