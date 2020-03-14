import pytest
from datetime import datetime, timedelta
from include.strategy import Strategy, Stock

MINUTES_PER_PERIOD = 5
PERIODS = 5
START_TIME = datetime(2020, 2, 13, 14, 0, 0)  # date choosen is irrelevant
END_TIME = START_TIME + timedelta(minutes=MINUTES_PER_PERIOD * (PERIODS-1))

@pytest.fixture(scope="module")
def strategy():
    global END_TIME
    strategy = Strategy("TEST", PERIODS, MINUTES_PER_PERIOD)
    high_prices = [100, 120, 130, 145, 90]
    low_prices = [80, 50, 90, 95, 65]
    close_prices = [90, 95, 112, 136, 70]
    timestamp = START_TIME
    for i in range(0,PERIODS):
        stock_data = {
            Stock.OPEN_INDEX: 100,
            Stock.HIGH_INDEX: high_prices[i],
            Stock.LOW_INDEX: low_prices[i],
            Stock.CLOSE_INDEX: close_prices[i],
            Stock.VOLUME_INDEX: 100,
        }
        strategy.addData(timestamp.strftime("%Y-%m-%d %H:%M:%S"), stock_data)
        if i < PERIODS-1:   # skip last
            timestamp = timestamp + timedelta(minutes=MINUTES_PER_PERIOD)
    return strategy
    
@pytest.fixture(scope="module")
def start_time():
    return START_TIME

@pytest.fixture(scope="module")
def end_time():
    return END_TIME

# Dates function tests
def test_format_date(strategy, start_time):
    date_str = strategy.formatDate(start_time)
    assert type(date_str) is str
    assert date_str == start_time.strftime("%Y-%m-%d %H:%M:%S")

def test_get_date_from_string(strategy):
    date_obj = strategy.getDatetimeFromStr("2020-02-17 14:00:00")
    assert type(date_obj) is datetime
    assert date_obj.date() == datetime(2020, 2, 17, 14, 0, 0).date()

def test_get_date_from_string_wrong_format(strategy):
    with pytest.raises(ValueError):     # check if exception is thown
        strategy.getDatetimeFromStr("2020/02/17 14:00:00")

# Calc functions tests
def test_calc_k_percent(strategy):
    k_perc = strategy.calcKPercent(100, 111, 86)
    expected = (100 - 86)/(111 - 86) * 100
    assert k_perc == expected

def test_get_low_high(strategy, start_time, end_time):
    real = strategy.getLowHigh(end_time, start_time)
    assert "low" in real
    assert "high" in real
    assert real["low"] == 50
    assert real["high"] == 145

#def test_get_moving_average(strategy):

    
