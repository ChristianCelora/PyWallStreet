import sys 
import os
import math
import json
import threading, time
import pytz
from datetime import datetime, timedelta
from include.strategy import Stock, Strategy
from include.logger import Logger
from include.market import Market, Wallet

"""def getAlphaVantageKey() -> str:
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    json_data = ""
    #read file
    with open( os.path.join(script_dir, "alpaca_api_key.json"), "r") as f:
        json_data = json.load(f)
    #get JSON data
    if not "key" in json_data:
        raise Exception("chiave AlphaVantage non trovata")
    #get key
    alpha_key = json_data["key"]

    return alpha_key"""

def getAlpacaKey() -> dict:
    script_dir = os.path.dirname(__file__) #absolute dir the script is in
    json_data = ""
    alpaca_key = {}
    #read file
    with open( os.path.join(script_dir, "alpaca_api_key.json"), "r") as f:
        json_data = json.load(f)
    #get JSON data
    if (not "key" in json_data) or (not "secret_key" in json_data):
        raise Exception("chiave Alpaca non trovata")
    #get key
    alpaca_key["key"] = json_data["key"]
    alpaca_key["secret_key"] = json_data["secret_key"]

    return alpaca_key

"""
def formatDate(date: datetime) -> datetime: # arrotondo ai 5 min precedenti
    if str(date.min)[1] < 5:
        minute = str(date.min)[0]."0"
    else:
        minute = str(date.min)[0]."5"
    format_date = datetime(date.year, date.month, date.day, date.hour, int(minute), 00)
    return format_date
"""

def main():
    MIN_INTERVAL = 5
    MINIUM_PERIODS = 10
    WAIT_TIME_SECONDS = MIN_INTERVAL * 60
    #WAIT_TIME_SECONDS = 4 # test
    data_key = "Time Series ("+str(MIN_INTERVAL)+"min)"
    stocks = sys.argv
    if len(stocks) < 2:
        raise Exception("No stock passed")
    
    #alpha_key = getAlphaVantageKey()
    alpaca_key = getAlpacaKey()
    #logger = Logger( os.path.join(os.path.dirname(__file__), "Log") )
    logger = None
    mywallet = Wallet(alpaca_key["key"], alpaca_key["secret_key"], logger)
    wallStreet = Market(alpaca_key["key"], alpaca_key["secret_key"], mywallet)
    strategies = []
    for i in range(1, len(stocks)):
        strategies.append(Strategy(stocks[i], MIN_INTERVAL, MINIUM_PERIODS))

    ticker = threading.Event()
    current_time = datetime.now()
    script_time = 0
    wait_time = 0
    market_close = wallStreet.getMarketCloseDatetime()
    if market_close is None:
        exit("Market close time not valid")
    print("Market will close at: "+market_close.strftime("%m/%d/%Y, %H:%M:%S"))
    while not ticker.wait(wait_time - script_time):
        start_time = time.time()
        wait_time = WAIT_TIME_SECONDS
        timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
        print(timestamp)
        if wallStreet.isMarketOpen():
            time_diff = market_close - datetime.utcnow().replace(tzinfo=pytz.utc) # time to market close  (should go in strategy)
            if int(time_diff.seconds//60) < 10: # if less than 10 min remaining sell all
                break
            print("Market open")
            for st in strategies:
                print("Stock:",st.name)
                stock_data = wallStreet.getStockData(st.name, MIN_INTERVAL, timestamp)
                if not st.name in stock_data:
                    raise Exception("Errore recupero dati stock ("+st.name+")")   
                if len(stock_data[st.name]) > 0:
                    last_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stock_data[st.name][0]["t"]))
                    print("last timestamp data:", last_timestamp)
                    isAdded = st.addData(last_timestamp, stock_data[st.name][0])
                    if isAdded: # check if we have new data
                        action = st.action()
                        invested = mywallet.getStock(st.name)
                        if action < 0:
                            print("Overbought market.")
                            if invested > 0:
                                try:
                                    gains = wallStreet.sellStock(st.name, MIN_INTERVAL)
                                    print("Sold:",invested,"qty. Gained:",gains,"EUR. New balance", mywallet.getBudget())
                                except Exception as e:
                                    print(str(e))
                        elif action > 0:
                            print("Oversold market.")
                            if invested == 0:
                                try:
                                    qty_bought = wallStreet.buyStock(st.name, MIN_INTERVAL, math.floor(mywallet.getBudget()/len(strategies)) )
                                    print("Bought:",qty_bought,"qty")
                                except Exception as e:
                                    print(str(e))
                        else:
                            print("Wait")
                    else:
                        print("Barra già presente per", st.name)
        else:
            print("Market closed")
        current_time = current_time + timedelta(minutes=MIN_INTERVAL)
        script_time = time.time() - start_time

    #sell everithing left
    for st in strategies:
        invested = mywallet.getStock(st.name)
        if invested > 0:
            try:
                wallStreet.sellStock(st.name, MIN_INTERVAL)
            except Exception as e:
                print(str(e))

    sys.exit(1)

if __name__ == "__main__":
    main()

