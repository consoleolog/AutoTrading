import unittest

import utils
from constants import TimeFrame


class DataTest(unittest.TestCase):

    def testCreateSubData(self):
        ticker = "BTC/KRW"
        timeframe = TimeFrame.MINUTE_15

        data = utils.create_sub_data(ticker, timeframe)
        for i in data:
            print(i)
        (MACD_Bullish,
         MACD_Bearish) = utils.parse_data(data,
                                       returns=("MACD_Bullish", "MACD_Bearish"))
        print(MACD_Bullish)
        print(MACD_Bearish)