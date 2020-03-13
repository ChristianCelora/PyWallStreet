import pytest
from datetime import datetime, timedelta
from include.strategy import Strategy, Stock

# INIT
MINUTES_PERIOD = 5
test_stock = Strategy("TEST", 10, MINUTES_PERIOD)

def test_calc_k_percent():
    k_perc = test_stock.calcKPercent(100, 111, 86)
    expected = (100 - 86)/(111 - 86) * 100
    assert k_perc == expected

def test_get_low_high():
    # init
    high = 0
    low = 1000
    now = datetime(2020, 2, 13, 14, 0, 0)   # date choosen is irrelevant
    timestamp = now
    for i in range(0,5):
        state_high = 100 + 5*i
        state_low = 100 - 5*i
        stock_data = {
            Stock.OPEN_INDEX: 100,
            Stock.HIGH_INDEX: state_high,
            Stock.LOW_INDEX: state_low,
            Stock.CLOSE_INDEX: 100,
            Stock.VOLUME_INDEX: 100,
        }
        test_stock.addData(timestamp.strftime("%Y-%m-%d %H:%M:%S"), stock_data)
        if state_low < low:
            low = state_low
        if state_high > high:
            high = state_high
        if i < 4:   # skip last
            timestamp = timestamp + timedelta(minutes=MINUTES_PERIOD)
    # test
    real = test_stock.getLowHigh(timestamp, now)
    assert low == real["low"]
    assert high == real["high"]

    
