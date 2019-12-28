import requests
import math
from .logger import Logger

# manage budget and stocks holdings (logs every transaction)
class Wallet:
    def __init__(self, starting_budget: float, log_obj: Logger):
        self.__budget = starting_budget
        self.__stocks = {}
        self.__logger = log_obj

    def __updateWallet(self, stock: str, qty: float, price: float):
        if not stock in self.__stocks:
            self.__stocks[stock] = 0
        self.__stocks[stock] = self.__floorTwoDec(self.__stocks[stock] + qty)

    def __floorTwoDec(self, val: float) -> float:
        return round(math.floor(val * 100) / 100.0, 2)
    
    def __updateBudget(self, val: float):
        self.__budget = self.__floorTwoDec(self.__budget + val)
        print("new budget:", self.__budget)

    def buyStock(self, stock: str, qty: float, price: float):
        self.__updateWallet(stock, qty, price)
        self.__updateBudget(qty * price * -1)
        if not self.__logger is None:
            self.__logger.log_action(stock, "BUY", qty, price, self.__budget)

    def sellStock(self, stock: str, qty: float, price: float):   
        self.__updateWallet(stock, qty*-1, price)
        self.__updateBudget(qty * price)
        if not self.__logger is None:
            self.__logger.log_action(stock, "SELL", qty, price, self.__budget)

    def getStock(self, stock: str) -> float:
        if not stock in self.__stocks:
            return 0
        else:
            return float(self.__stocks[stock])
            
    def getBudget(self) -> float:
        return self.__budget

# manage API calls with the stock market
class Market:
    def __init__(self, alpha_key: str, wallet: Wallet):
        self.__alpha_key = alpha_key
        self.__wallet = wallet

    def __alphaVantageRequest(self, params: dict) -> dict:
        res = requests.get("https://www.alphavantage.co/query", params=params)
        if res.status_code != 200:
            raise Exception("errore", res.status_code)
        return res.json()

    def getStockHistory(self, stock: str, interval: int) -> dict:
        params = {"function": "TIME_SERIES_INTRADAY", "symbol": stock, "interval": str(interval)+"min", 
            "apikey": self.__alpha_key, "outputsize": "compact"}
        return self.__alphaVantageRequest(params)

    def getRealTimeQuotes(self, stock: str) -> dict:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": self.__alpha_key}
        return self.__alphaVantageRequest(params)

    def getRealTimePrice(self, stock: str) -> float:
        data = self.getRealTimeQuotes(stock)
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
        else:
            return -1

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
        
    
    
