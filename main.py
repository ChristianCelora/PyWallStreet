import sys 
import os
import math
import json
import threading, time
from datetime import datetime, timedelta
from include.strategy import Stock, Strategy
from include.logger import Logger
from include.market import Market, Wallet

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

def main():
    MIN_INTERVAL = 5
    MINIUM_PERIODS = 10
    #WAIT_TIME_SECONDS = 60
    WAIT_TIME_SECONDS = 4 # test
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"
    stocks = sys.argv
    if len(stocks) < 2:
        raise Exception("No stock passed")
    
    alpha_key = getAlphaVantageKey()
    alpaca_key = getAlpacaKey()
    logger = Logger(os.path.dirname(__file__) + "\\Log")
    mywallet = Wallet(alpaca_key["key"], alpaca_key["secret_key"], logger)
    wallStreet = Market(alpaca_key["key"], alpaca_key["secret_key"], mywallet)
    strategies = []
    for i in range(1, len(stocks)):
        strategies.append(Strategy(stocks[i], MIN_INTERVAL, MINIUM_PERIODS))

    ticker = threading.Event()
    while not ticker.wait(WAIT_TIME_SECONDS):
        for st in strategies:
            print(time.ctime())
            print("Stock:",st.name)
            res_data = wallStreet.getStockData(st.name, MIN_INTERVAL)
            if not data_key in res_data:
                raise Exception("Errore recupero dati stock ("+st.name+")")
            recent_timestamp = list(res_data[data_key].keys())[0]
            isAdded = st.addData(recent_timestamp, res_data[data_key][recent_timestamp])
            if isAdded: # check if we have new data
                action = st.action()
                invested = mywallet.getStock(st.name)
                if action < 0:
                    print("Overbought market.")
                    if invested > 0:
                        gains = wallStreet.sellStock(st.name)
                        print("Sold:",invested,"qty. Gained:",gains,"EUR. New balance", mywallet.getBudget())
                elif action > 0:
                    print("Oversold market.")
                    if invested != 0:
                        qty_bought = wallStreet.buyStock(st.name, math.floor(mywallet.getBudget()/len(strategies)) )
                        print("Bought:",qty_bought,"qty")
                else:
                    print("Wait")
        
    sys.exit(1)

if __name__ == "__main__":
    main()

