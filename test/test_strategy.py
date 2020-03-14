import pytest
from datetime import datetime, timedelta
from include.strategy import Strategy, Stock

MINUTES_PERIOD = 5
@pytest.fixture(scope="module")
def strategy():
    strategy = Strategy("TEST", 10, MINUTES_PERIOD)
    return strategy

def test_calc_k_percent(strategy):
    k_perc = strategy.calcKPercent(100, 111, 86)
    expected = (100 - 86)/(111 - 86) * 100
    assert k_perc == expected

def test_format_date(strategy):
    timestamp = datetime.now()
    date_str = strategy.formatDate(timestamp)
    assert type(date_str) is str
    assert date_str == timestamp.strftime("%Y-%m-%d %H:%M:%S")

def test_get_date_from_string(strategy):
    date_obj = strategy.getDatetimeFromStr("2020-02-17 14:00:00")
    assert type(date_obj) is datetime
    assert date_obj.date() == datetime(2020, 2, 17, 14, 0, 0).date()

def test_get_date_from_string_wrong_format(strategy):
    with pytest.raises(ValueError): 
        strategy.getDatetimeFromStr("2020/02/17 14:00:00")

def test_get_low_high(strategy):
    # init
    high = 0
    low = 1000
    now = datetime(2020, 2, 13, 14, 0, 0)   # date choosen is irrelevant
    high_prices = [100, 120, 130, 145, 90]
    low_prices = [80, 50, 90, 95, 65]
    timestamp = now
    for i in range(0,len(high_prices)):
        stock_data = {
            Stock.OPEN_INDEX: 100,
            Stock.HIGH_INDEX: high_prices[i],
            Stock.LOW_INDEX: low_prices[i],
            Stock.CLOSE_INDEX: 100,
            Stock.VOLUME_INDEX: 100,
        }
        strategy.addData(timestamp.strftime("%Y-%m-%d %H:%M:%S"), stock_data)
        if i < 4:   # skip last
            timestamp = timestamp + timedelta(minutes=MINUTES_PERIOD)
    # test
    real = strategy.getLowHigh(timestamp, now)
    assert "low" in real
    assert "high" in real
    assert real["low"] == min(low_prices)
    assert real["high"] == max(high_prices)

    
