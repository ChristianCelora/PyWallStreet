from datetime import datetime, timedelta

# Simple stock
class Stock:
    #alpaca trading indexes
    OPEN_INDEX = "o"
    HIGH_INDEX = "h"
    LOW_INDEX = "l"
    CLOSE_INDEX = "c"
    VOLUME_INDEX = "v"

    def __init__(self, key: str, time: str, data: dict):
        self.name = key
        self.time = time
        self.open = float(data[self.OPEN_INDEX])
        self.high = float(data[self.HIGH_INDEX])
        self.low = float(data[self.LOW_INDEX])
        self.close = float(data[self.CLOSE_INDEX])
        self.volume = float(data[self.VOLUME_INDEX])

# Investing strategy
class Strategy:
    def __init__(self, stock: str, inter: int, periods: int):
        self.periods = periods
        self.min_interval = inter
        self.data = {}
        self.name = stock

    def addData(self, time: str, stock_data: dict):
        if time not in self.data:
            self.data[time] = Stock(self.name, time, stock_data)
            return True
        return False

    def action(self) -> int:
        if len(self.data.keys()) > self.periods:  # Do nothin until you reach min periods 
            stoc_index = self.getStochasticIndex()
            mov_avg = self.getMovingAverage()
            last_period = list(self.data.keys())[-1]
            #if stoc_index["%K"] >= 80 and mov_avg > self.data[last_period].close:
            if stoc_index["%K"] >= 80:
                return -1
            #elif stoc_index["%K"] <= 20 and mov_avg < self.data[last_period].close:
            elif stoc_index["%K"] <= 20:
                return 1
        return 0

    def getMovingAverage(self) -> float:
        sma = 0
        timestamps = list(self.data.keys())[-self.periods:]
        for i in range(0, self.periods):
            sma += self.data[timestamps[i]].close

        return round(sma / self.periods, 2)

    def getStochasticIndex(self) -> dict:
        #calculate start period and end period
        last_period = list(self.data.keys())[-1]
        now = self.getDatetimeFromStr(last_period)
        past = now - timedelta(minutes=self.min_interval*self.periods)
        now_str = self.formatDate(now)
        past_str = self.formatDate(past)
        if not past_str in self.data:
            raise Exception(past_str," not in stock data")
        limits = self.getLowHigh(now, past)
        #calculate stock %K
        perc_k = self.calcKPercent(float(self.data[now_str].close), float(limits["low"]), float(limits["high"]))
        #calculate stock %D
        perc_d = 50

        return {"%K": perc_k, "%D": perc_d}  

    # date_str: "YYYY-MM-DD HH:MM:SS"
    def getDatetimeFromStr(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")

    def formatDate(self, date: datetime) -> str:
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def getLowHigh(self, now: datetime, past: datetime) -> dict:
        low = self.data[self.formatDate(past)].low
        high = self.data[self.formatDate(past)].high

        next_data = past
        while self.formatDate(next_data) != self.formatDate(now):
            next_data = next_data + timedelta(minutes=5)
            next_data_str = self.formatDate(next_data)
            if self.data[next_data_str].low < low:
                low = self.data[next_data_str].low
            if self.data[next_data_str].high > high:
                high = self.data[next_data_str].high

        return {"low": low, "high": high}

    def calcKPercent(self, closing_price: float, high: float, low: float) -> float:
        if low == high:
            return 50
        return (closing_price - low) / (high - low) * 100

    """def isUptrending(self) -> bool:
        keys = list(self.data.keys())
        return ( self.data[keys[0]].open - self.data[keys[len(keys)-1]].close < 0 )
    """