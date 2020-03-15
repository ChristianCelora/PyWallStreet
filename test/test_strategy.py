import pytest
import statistics
import copy
from datetime import datetime, timedelta
from include.strategy import Strategy, Stock

# INIT
MINUTES_PER_PERIOD = 5
PERIODS = 5
START_TIME = datetime(2020, 2, 13, 14, 0, 0)  # date choosen is irrelevant
END_TIME = START_TIME + timedelta(minutes=MINUTES_PER_PERIOD * (PERIODS-1))
high_prices = [100, 120, 130, 145, 90]
low_prices = [80, 50, 90, 95, 65]
close_prices = [90, 95, 112, 136, 70]

@pytest.fixture(scope="module")
def strategy():
    global high_prices
    global low_prices
    global close_prices

    strategy = Strategy("TEST", PERIODS, MINUTES_PER_PERIOD)
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
    date_str = strategy.getStrFromDatetime(start_time)
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
    global high_prices
    global low_prices

    real = strategy.getLowHigh(end_time, start_time)
    assert "low" in real
    assert "high" in real
    assert real["low"] == min(low_prices)
    assert real["high"] == max(high_prices)

def test_get_moving_average(strategy, end_time):
    global close_prices

    expected_sma = round(statistics.mean(close_prices), 2)
    assert strategy.getMovingAverage() == expected_sma
    st2 = copy.deepcopy(strategy) 
    new_close_price = 125
    new_close_prices = copy.deepcopy(close_prices) 
    new_close_prices.append(new_close_price)
    end_time += timedelta(minutes=MINUTES_PER_PERIOD)
    stock_data = {
            Stock.OPEN_INDEX: 100,
            Stock.HIGH_INDEX: 100,
            Stock.LOW_INDEX: 100,
            Stock.CLOSE_INDEX: new_close_price,
            Stock.VOLUME_INDEX: 100,
        }
    st2.addData(end_time.strftime("%Y-%m-%d %H:%M:%S"), stock_data)
    new_expected_sma = round(statistics.mean(new_close_prices[1:]), 2)
    assert st2.getMovingAverage() == new_expected_sma





    
