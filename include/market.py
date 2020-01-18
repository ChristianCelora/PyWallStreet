import requests
import math
import alpaca_trade_api as alpaca
from datetime import datetime
from .logger import Logger
from .strategy import Stock


# manage budget and stocks holdings (logs every transaction)
class Wallet:
    def __init__(self, al_key:str, al_secret:str, log_obj: Logger):
        #self.__stocks = {}
        self.__logger = log_obj
        self.__alpaca_key = {}
        self.__alpaca_key["key"] = al_key
        self.__alpaca_key["secret"] = al_secret
        self.__budget = self.__getAlpacaAccountBudget()

    def __alpacaRequest(self, method: str, url: str, header: dict, data: dict) -> dict:
        alpaca_api_url = "https://paper-api.alpaca.markets/"
        if method == "GET":
            res = requests.get(alpaca_api_url + url, headers=header)
        elif method == "POST":
            res = requests.post(alpaca_api_url + url, headers=header, json=data)
        else:
            raise Exception("invaid method", method)

        if res.status_code != 200:
            raise Exception("errore", res.status_code, "content", res.content)
        return res.json()

    def __getAlpacaAccountBudget(self) -> float:
        head = {"APCA-API-KEY-ID": self.__alpaca_key["key"], "APCA-API-SECRET-KEY": self.__alpaca_key["secret"],
            "Content-Type": "application/json"}
        account = self.__alpacaRequest("GET", "v2/account", head, None)
        return float(account["cash"])

    def __newOrder(self, stock: str, qty: float, buy_flag: bool) -> float:
        head = {"APCA-API-KEY-ID": self.__alpaca_key["key"],"APCA-API-SECRET-KEY": self.__alpaca_key["secret"],
            "Content-Type": "application/json"}
        if buy_flag: 
            side = "buy"
        else:
            side = "sell"
        data = {"symbol":stock, "qty":qty, "side":side, "type":"market", "time_in_force":"day"}
        order = self.__alpacaRequest("POST", "v2/orders", head, data)
        return order["id"]

    """def __updateWallet(self, stock: str, qty: float, price: float):
        if not stock in self.__stocks:
            self.__stocks[stock] = 0
        self.__stocks[stock] = self.__floorTwoDec(self.__stocks[stock] + qty)"""

    def __floorTwoDec(self, val: float) -> float:
        return round(math.floor(val * 100) / 100.0, 2)
    
    def __updateBudget(self):
        self.__budget = self.__getAlpacaAccountBudget()

    def buyStock(self, stock: str, qty: float, price: float):
        self.__updateBudget()
        self.__newOrder(stock, qty, True)
        if not self.__logger is None:
            self.__logger.log_action(stock, "BUY", qty, price, self.__budget)

    def sellStock(self, stock: str, qty: float, price: float):   
        self.__updateBudget()
        self.__newOrder(stock, qty, False)
        if not self.__logger is None:
            self.__logger.log_action(stock, "SELL", qty, price, self.__budget)

    def getStock(self, stock: str) -> float:
        head = {"APCA-API-KEY-ID": self.__alpaca_key["key"],"APCA-API-SECRET-KEY": self.__alpaca_key["secret"]}
        try:
            position = self.__alpacaRequest("GET", "v2/positions/"+stock, head, None)
            return position["qty"]
        except:
            return 0

    def getBudget(self) -> float:
        return self.__budget

# manage API calls with the stock market
class Market:
    def __init__(self, al_key:str, al_secret:str, wallet: Wallet):
        #self.__alpha_key = alpha_key
        self.__alpaca_key = {}
        self.__alpaca_key["key"] = al_key
        self.__alpaca_key["secret"] = al_secret
        self.__wallet = wallet

    """def __alphaVantageRequest(self, params: dict) -> dict:
        res = requests.get("https://www.alphavantage.co/query", params=params)
        if res.status_code != 200:
            raise Exception("errore", res.status_code)
        return res.json()

    def getStockHistory(self, stock: str, interval: int) -> dict:
        params = {"function": "TIME_SERIES_INTRADAY", "symbol": stock, "interval": str(interval)+"min", 
            "apikey": self.__alpha_key, "outputsize": "compact"}
        return self.__alphaVantageRequest(params)   # API times are in GTM-5 tiemzone

    def getRealTimeQuotes(self, stock: str) -> dict:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": self.__alpha_key}
        return self.__alphaVantageRequest(params)

    def getRealTimePrice(self, stock: str) -> float:
        data = self.getRealTimeQuotes(stock)
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
        else:
            return -1"""
    def __alpacaRequest(self, method: str, url: str, header: dict, data: dict) -> dict:
        alpaca_api_url = "https://data.alpaca.markets/"
        if method == "GET":
            if data is None:
                res = requests.get(alpaca_api_url + url, headers=header)
            else:
                res = requests.get(alpaca_api_url + url, headers=header, params=data)
        elif method == "POST":
            res = requests.post(alpaca_api_url + url, headers=header, json=data)
        else:
            raise Exception("invaid method", method)

        if res.status_code != 200:
            raise Exception("errore", res.status_code, "content", res.content)
        return res.json()
    
    def getStockData(self, stock: str, timestamp: str) -> dict:
        head = {"APCA-API-KEY-ID": self.__alpaca_key["key"],"APCA-API-SECRET-KEY": self.__alpaca_key["secret"],
            "Content-Type": "application/json"}
        params = {"symbols": stock, "limit": 1, "start": timestamp}
        return self.__alpacaRequest("GET", "v1/bars/5Min", head, params)

    def getRealTimePrice(self, stock: str) -> float:
        head = {"APCA-API-KEY-ID": self.__alpaca_key["key"],"APCA-API-SECRET-KEY": self.__alpaca_key["secret"],
            "Content-Type": "application/json"}
        params = {"symbols": stock, "limit": 1}
        data = self.__alpacaRequest("GET", "v1/bars/5Min", head, params)
        if not stock in data:
            return 0
        stock = Stock(stock, 0, data[stock])
        return stock.close

    def __floorTwoDec(self, val: float) -> float:
        return math.floor(val * 100) / 100.0
    
    def buyStock(self, stock: str, budget: float) -> float:
        price = self.getRealTimePrice(stock)
        if price < 0:
            return 0
        qty_bought = self.__floorTwoDec(budget / price)
        self.__wallet.buyStock(stock, qty_bought, price)
        return qty_bought

    def sellStock(self, stock: str, qty = -1) -> float:
        if qty == -1:   # if -1 sell all qty
            qty = self.__wallet.getStock(stock)
        price = self.getRealTimePrice(stock)
        return_gain = self.__floorTwoDec(qty * price)
        self.__wallet.sellStock(stock, qty, price)
        return return_gain
    
        
    
    
