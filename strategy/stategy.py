from datetime import datetime, timedelta

class Stock:
    OPEN_INDEX = "1. open"
    HIGH_INDEX = "2. high"
    LOW_INDEX = "3. low"
    CLOSE_INDEX = "4. close"
    VOLUME_INDEX = "5. volume"

    def __init__(self, key: str, time: str, data: dict):
        self.name = key
        self.time = time
        self.open = data[self.OPEN_INDEX]
        self.high = data[self.HIGH_INDEX]
        self.low = data[self.LOW_INDEX]
        self.close = data[self.CLOSE_INDEX]
        self.volume = data[self.VOLUME_INDEX]

class Strategy:
    def __init__(self, key: str, stock_data: dict, periods: int):
        self.periods = periods
        self.data = {}
        i = 0
        for datetime in stock_data:
            self.data[datetime] = Stock(key, datetime, stock_data[datetime])
            if (i > periods):
                break
            i += 1
        print(len(self.data))

    def action(self) -> int:
        stoc_index = self.getStochasticIndex()
        print(stoc_index)
        if stoc_index["%K"] >= 80:
            return -1
        elif stoc_index["%K"] <= 20:
            return 1
        return 0

    def getStochasticIndex(self) -> dict:
        #calculate start period and end period
        first_period = list(self.data.keys())[0]
        fp_arr = first_period.split(" ")
        fp_date = fp_arr[0].split("-")
        fp_time = fp_arr[1].split(":")
        now = datetime(int(fp_date[0]), int(fp_date[1]), int(fp_date[2]), int(fp_time[0]), int(fp_time[1]), int(fp_time[2]), 000000)
        past = now - timedelta(minutes=5*self.periods)
        now_str = self.formatDate(now)
        past_str = self.formatDate(past)
        if not past_str in self.data:
            raise Exception(past_str," not in stock data")
        limits = self.getLowHigh(now, past)
        print(limits)
        #calculate stock %K
        perc_k = self.calcKPercent(float(self.data[now_str].close), float(limits["low"]), float(limits["high"]))
        #calculate stock %D
        perc_d = 50

        return {"%K": perc_k, "%D": perc_d}  

    def formatDate(self, date) -> str:
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def getLowHigh(self, now, past) -> dict:
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

    def calcKPercent(self, closing_price: float, high: float, low: float):
        return (closing_price - low) / (high - low) * 100