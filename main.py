import sys 
import os
import json
import threading, time
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from include.strategy import Stock, Strategy
from include.logger import Logger
from include.market import Market

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
    MINIUM_PERIODS = 14
    #WAIT_TIME_SECONDS = 60
    WAIT_TIME_SECONDS = 4 #test
    STARTING_BUDGET = 1000
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"
    budget = STARTING_BUDGET
    stocks = sys.argv
    stocks = ["file", "SPRT"]
    if len(stocks) < 2:
        raise Exception("No stock passed")
    
    alpha_key = getAlphaVantageKey()
    wallStreet = Market(alpha_key)
    logger = Logger(os.path.dirname(__file__) + "\\Log")
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
            st.addData(res_data[data_key])
            action = st.action()
            real_time_data = wallStreet.getRealTimeQuotes(st.name)
            price = wallStreet.getRealTimePrice(real_time_data)
            if price > 0:
                if action < 0:
                    print("Overbought  market. SELL!")
                    if st.invested > 0:
                        qty_bought = st.invested
                        gains = st.sellStock(price)
                        budget += gains
                        logger.log_action(st.name, "SELL", qty_bought, price, budget)
                        print("Sold:",qty_bought,"qty. Gained:",gains,"EUR. New balance", budget)
                elif action > 0:
                    print("Oversold market. BUY!")
                    if st.invested != 0:
                        qty_bought = st.buyStock(price, budget/5)
                        budget -= qty_bought * price
                        logger.log_action(st.name, "BUY", qty_bought, price, budget)
                        print("Bought:",qty_bought,"qty")
                else:
                    print("Wait")
            else:
                print("real time price not available for", st.name)
        
    sys.exit(1)

if __name__ == "__main__":
    main()

