import requests
import math
from datetime import datetime, timedelta
#import dateutil.parser
from .logger import Logger
from .strategy import Stock


# manage budget and stocks holdings (logs every transaction)
class Wallet:
    def __init__(self, al_key:str, al_secret:str, log_obj: Logger):
        #self.__stocks = {}
        self.__logger = log_obj
        self.__alpacaapi = AlpacaAPI(al_key, al_secret)
        self.__budget = self.__alpacaapi.getAlpacaAccountBudget()

    def __floorTwoDec(self, val: float) -> float:
        return round(math.floor(val * 100) / 100.0, 2)
    
    def __updateBudget(self):
        self.__budget = self.__alpacaapi.getAlpacaAccountBudget()

    def buyStock(self, stock: str, qty: int, price: float):
        self.__updateBudget()
        self.__alpacaapi.newOrder(stock, qty, True)
        if not self.__logger is None:
            self.__logger.log_action(stock, "BUY", qty, price, self.__budget)

    def sellStock(self, stock: str, qty: int, price: float):   
        self.__updateBudget()
        self.__alpacaapi.newOrder(stock, qty, False)
        if not self.__logger is None:
            self.__logger.log_action(stock, "SELL", qty, price, self.__budget)

    def getStock(self, stock: str) -> int:
        try:
            position = self.__alpacaapi.getPosition(stock)
            return int(position["qty"])
        except:
            return 0

    def getBudget(self) -> float:
        return self.__budget

# manage API calls with the stock market
class Market:
    def __init__(self, al_key:str, al_secret:str, wallet: Wallet):
        #self.__alpha_key = alpha_key
        self.__alpacaapi = AlpacaAPI(al_key, al_secret)
        self.__wallet = wallet      

    def __floorTwoDec(self, val: float) -> float:
        return math.floor(val * 100) / 100.0

    def getStockData(self, stock: str, interval: int, timestamp: datetime) -> dict:
        #return self.__alpacaapi.getStockData(stock, interval, timestamp)
        return self.__alpacaapi.getStockData(stock, interval)

    def getRealTimePrice(self, stock: str, interval: int) -> float:
        data = self.__alpacaapi.getRealTimePrice(stock, interval)
        if not stock in data:
            return 0
        stock = Stock(stock, 0, data[stock][0])
        return stock.close
    
    def buyStock(self, stock: str, interval: int, budget: float) -> float:
        price = self.getRealTimePrice(stock, interval)
        if price <= 0:
            return 0
        qty_bought = int(self.__floorTwoDec(budget / price))
        self.__wallet.buyStock(stock, qty_bought, price)
        return qty_bought

    def sellStock(self, stock: str, interval: int, qty = -1) -> float:
        if qty == -1:   # if -1 sell all qty
            qty = self.__wallet.getStock(stock)
        price = self.getRealTimePrice(stock, interval)
        return_gain = self.__floorTwoDec(qty * price)
        self.__wallet.sellStock(stock, qty, price)
        return return_gain

    def isMarketOpen(self) -> bool:
        market_time = self.__alpacaapi.getMarketTimes()
        if "is_open" in market_time:
            return market_time["is_open"]
        return False

    def getMarketCloseDatetime(self) -> datetime:
        market_time = self.__alpacaapi.getMarketTimes()
        if not "next_close" in market_time:
            return None
        try:
            date = market_time["next_close"][:-6]
            timez = market_time["next_close"][-6:]
            date_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            if timez[0] == "+":
                date_obj = date_obj + timedelta(minutes=int(timez[-2:]))
                date_obj = date_obj + timedelta(hours=int(timez.split(":")[0]))
            elif timez[0] == "-":
                date_obj = date_obj - timedelta(minutes=int(timez[-2:]))
                date_obj = date_obj - timedelta(hours=int(timez.split(":")[0]))
        except Exception as e:
            return None

        return date_obj

class AlpacaAPI:
    ALPACA_PAPER_URL = "https://paper-api.alpaca.markets/"
    ALPACA_DATA_URL = "https://data.alpaca.markets/"
    def __init__(self, al_key:str, al_secret:str):
        #self.__alpha_key = alpha_key
        self.__alpaca_key = {}
        self.__alpaca_key["key"] = al_key
        self.__alpaca_key["secret"] = al_secret
    # Account
    def getAlpacaAccountBudget(self) -> float:
        head = self.__getHeader()
        account = self.__alpacaRequest("GET", self.ALPACA_PAPER_URL+"v2/account", head, None)
        return float(account["cash"])

    def getPosition(self, stock: str) -> float:
        head = self.__getHeader()
        return self.__alpacaRequest("GET", self.ALPACA_PAPER_URL+"v2/positions/"+stock, head, None)

    # Market
    def newOrder(self, stock: str, qty: int, buy_flag: bool) -> float:
        head = self.__getHeader()
        if buy_flag: 
            side = "buy"
        else:
            side = "sell"
        data = {"symbol":stock, "qty":qty, "side":side, "type":"market", "time_in_force":"day"}
        order = self.__alpacaRequest("POST", self.ALPACA_PAPER_URL+"v2/orders", head, data)
        return order["id"]

    def getStockData(self, stock: str, interval: int) -> dict:
        head = self.__getHeader()
        params = {"symbols": stock, "limit": 1}
        str_interval = interval+"Min"
        return self.__alpacaRequest("GET", self.ALPACA_DATA_URL+"v1/bars/"+str_interval, head, params)

    def getRealTimePrice(self, stock: str, interval: int) -> float:
        head = self.__getHeader()
        params = {"symbols": stock, "limit": 1}
        str_interval = interval+"Min"
        return self.__alpacaRequest("GET", self.ALPACA_DATA_URL+"v1/bars/"+str_interval, head, params)
        
    def getMarketTimes(self) -> dict:
        head = self.__getHeader()
        return self.__alpacaRequest("GET", self.ALPACA_PAPER_URL+"v2/clock", head, None)

    def __getHeader(self) -> dict:
        return {"APCA-API-KEY-ID": self.__alpaca_key["key"],"APCA-API-SECRET-KEY": self.__alpaca_key["secret"], 
            "Content-Type": "application/json"}

    def __alpacaRequest(self, method: str, url: str, header: dict, data: dict) -> dict:
        if method == "GET":
            if data is None:
                res = requests.get(url, headers=header)
            else:
                res = requests.get(url, headers=header, params=data)
        elif method == "POST":
            res = requests.post(url, headers=header, json=data)
        else:
            raise Exception("invaid method", method)

        if res.status_code != 200:
            raise Exception("errore", res.status_code, "content", res.content)
        return res.json()