import pytest
from include.strategy import Strategy

# INIT
test_stock = Strategy("TEST", 10, 5)

def test_first():
    assert 2 == 2

def test_calcKPercent():
    k_perc = test_stock.calcKPercent(100, 111, 86)
    expected = (100 - 86)/(111 - 86) * 100
    assert k_perc == expected
