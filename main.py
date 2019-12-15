import sys 
import os
import json
import requests
from datetime import datetime, timedelta

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

def formatDate(date) -> str:
    return date.strftime("%Y-%m-%d %H:%M:%S")

def getLowHigh(data: dict, now, past) -> dict:
    low_price_index = "3. low"
    high_price_index = "2. high"
    low = data[formatDate(past)][low_price_index]
    high = data[formatDate(past)][high_price_index]

    next_data = past
    while formatDate(next_data) != formatDate(now):
        next_data = next_data + timedelta(minutes=5)
        next_data_str = formatDate(next_data)
        if data[next_data_str][low_price_index] < low:
            low = data[next_data_str][low_price_index]
        if data[next_data_str][high_price_index] > high:
            high = data[next_data_str][high_price_index]

    return {"low": low, "high": high}

def calcKPercent(closing_price: float, high: float, low: float):
    return (closing_price - low) / (high - low) * 100

def getStochasticIndex(stock_data: dict) -> dict:
    perc_k = 50
    perc_d = 50
    periods = 14
    closing_price_index = "4. close"
    #calculate start period and end period
    first_period = list(stock_data.keys())[0]
    fp_arr = first_period.split(" ")
    fp_date = fp_arr[0].split("-")
    fp_time = fp_arr[1].split(":")
    now = datetime(int(fp_date[0]), int(fp_date[1]), int(fp_date[2]), int(fp_time[0]), int(fp_time[1]), int(fp_time[2]), 000000)
    past = now - timedelta(minutes=5*periods)
    now_str = formatDate(now)
    past_str = formatDate(past)
    if not past_str in stock_data:
        raise Exception(past_str," not in stock data")
    elif not now_str in stock_data:
        raise Exception(now_str," not in stock data")
    limits = getLowHigh(stock_data, now, past)
    print(limits)
    #calculate stock %K
    perc_k = calcKPercent(float(stock_data[now_str][closing_price_index]), float(limits["low"]), float(limits["high"]))
    #calculate stock %D
    
    return {"%K": perc_k, "%D": perc_d}    


def main():
    stock = "SRPT" #mock
    alpha_key = getAlphaVantageKey()
    res_data = getStockInfo(alpha_key, stock)
    #print(res_data)
    if not "Time Series (5min)" in res_data:
        raise Exception("Errore recupero dati stock ("+stock+")")
    stoc_index = getStochasticIndex(res_data["Time Series (5min)"])
    print(stoc_index)
    sys.exit(1)

if __name__ == "__main__":
    main()

