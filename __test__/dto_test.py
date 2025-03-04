import os
import sys
import unittest

import exchange
import utils
from constants import TimeFrame
from technical_indicator import EMA


class DTOTest(unittest.TestCase):
    def setUp(self):
        pass


    def testCreateEMADto(self):
        ticker = "BTC/KRW"
        timeframe = TimeFrame.MINUTE
        data = exchange.get_candles(ticker, timeframe)
        value = EMA(data["close"], 8)
        print(value)



