import requests

class Market:
    def __init__(self, alpha_key: str):
        self.alpha_key = alpha_key

    def alphaVantageRequest(self, params: dict) -> dict:
        res = requests.get("https://www.alphavantage.co/query", params=params)
        if res.status_code != 200:
            raise Exception("errore", res.status_code)
        return res.json()

    def getStockHistory(self, stock: str, interval: int) -> dict:
        params = {"function": "TIME_SERIES_INTRADAY", "symbol": stock, "interval": str(interval)+"min", 
            "apikey": self.alpha_key, "outputsize": "compact"}
        return self.alphaVantageRequest(params)

    def getRealTimeQuotes(self, stock: str) -> dict:
        params = {"function": "GLOBAL_QUOTE", "symbol": stock, "apikey": self.alpha_key}
        return self.alphaVantageRequest(params)

    def getRealTimePrice(self, data: dict) -> float:
        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            return float(data["Global Quote"]["05. price"])
        else:
            return -1