import sys 
import os
import json
import threading, time
import alpaca_trade_api as tradeapi
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

def main():
    MIN_INTERVAL = 5
    MINIUM_PERIODS = 10
    #WAIT_TIME_SECONDS = 60
    WAIT_TIME_SECONDS = 4 #test
    STARTING_BUDGET = 1000
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"
    stocks = sys.argv
    stocks = ["", "SPRT"]   #mock
    if len(stocks) < 2:
        raise Exception("No stock passed")
    
    alpha_key = getAlphaVantageKey()
    logger = Logger(os.path.dirname(__file__) + "\\Log")
    mywallet = Wallet(STARTING_BUDGET, logger)
    wallStreet = Market(alpha_key, mywallet)
    strategies = []
    for i in range(1, len(stocks)):
        strategies.append(Strategy(stocks[i], MIN_INTERVAL, MINIUM_PERIODS))

    ticker = threading.Event()
    while not ticker.wait(WAIT_TIME_SECONDS):
        for st in strategies:
            print(time.ctime())
            print("Stock:",st.name)
            res_data = wallStreet.getStockHistory(st.name, MIN_INTERVAL)
            if not data_key in res_data:
                raise Exception("Errore recupero dati stock ("+st.name+")")
            recent_timestamp = list(res_data[data_key].keys())[0]
            st.addData(recent_timestamp, res_data[data_key][recent_timestamp])
            action = st.action()
            invested = mywallet.getStock(st.name)
            if action < 0:
                print("Overbought  market. SELL!")
                if invested > 0:
                    gains = wallStreet.sellStock(st.name)
                    print("Sold:",invested,"qty. Gained:",gains,"EUR. New balance", mywallet.getBudget())
            elif action > 0:
                print("Oversold market. BUY!")
                if invested != 0:
                    qty_bought = wallStreet.buyStock(st.name, round(mywallet.getBudget()/5, 2) )
                    print("Bought:",qty_bought,"qty")
            else:
                print("Wait")
        
    sys.exit(1)

if __name__ == "__main__":
    main()

