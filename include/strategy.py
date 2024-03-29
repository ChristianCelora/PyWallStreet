from datetime import datetime, timedelta
from abc import ABC, abstractmethod

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
class AbstractStrategy(ABC):

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, stock: str, inter: int, periods: int):
        self.periods = periods
        self.min_interval = inter
        self.name = stock
        self.bars = []
        self.timestamps = []    # Keep track if the bar is alredy added

    def getDatetimeFromStr(self, date_str: str) -> datetime:
        return datetime.strptime(date_str, self.DATE_FORMAT)

    def getStrFromDatetime(self, date: datetime) -> str:
        return date.strftime(self.DATE_FORMAT)

    @abstractmethod
    def action(self) -> int:
        pass

class Strategy(AbstractStrategy):

    def addData(self, time: str, stock_data: dict):
        if not time in self.timestamps:
            self.bars.append(Stock(self.name, time, stock_data))
            self.timestamps.append(time)
            return True
        return False

    def action(self) -> int:
        if len(self.bars) > self.periods:  # Do nothin until you reach min periods 
            stoc_index = self.getStochasticIndex()
            mov_avg = self.getMovingAverage()
            if stoc_index["%K"] >= 80 and mov_avg > self.bars[-1].close:
            #if stoc_index["%K"] >= 80:
                return -1
            elif stoc_index["%K"] <= 20 and mov_avg < self.bars[-1].close:
            #elif stoc_index["%K"] <= 20:
                return 1
        return 0

    def getMovingAverage(self) -> float:
        if len(self.bars) < self.periods:
            return -1
        sma = 0
        # get only last n-th timestamps (n = number periods)
        for bar in self.bars[-self.periods:]:
            sma += bar.close
        return round(sma / self.periods, 2)

    def getStochasticIndex(self) -> dict:
        #calculate start period and end period
        last_bar = self.bars[-1]
        limits = self.getLowHigh()
        #calculate stock %K
        perc_k = self.calcKPercent(float(last_bar.close), float(limits["low"]), float(limits["high"]))
        #calculate stock %D
        perc_d = 50

        return {"%K": perc_k, "%D": perc_d}  

    def getLowHigh(self) -> dict:
        low = self.bars[-self.periods].low
        high = self.bars[-self.periods].high

        start = (self.periods-1)*-1
        for i in range(start, len(self.bars)): 
            if self.bars[i].low < low:
                low = self.bars[i].low
            if self.bars[i].high > high:
                high = self.bars[i].high

        return {"low": low, "high": high}

    def calcKPercent(self, closing_price: float, high: float, low: float) -> float:
        if low == high:
            return 50
        return (closing_price - low) / (high - low) * 100