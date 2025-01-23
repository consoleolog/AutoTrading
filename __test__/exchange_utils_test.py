import unittest

from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from utils import exchange_utils


class ExchangeUtilsTest(unittest.TestCase):
    def setUp(self):
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        LoggerFactory().set_stream_level(LoggerFactory.DEBUG)

    def test_get_ticker_info(self):
        ticker = "COMP/KRW"
        ticker_info = exchange_utils.get_ticker_info(ticker)
        self.logger.debug(ticker_info)

    def test_get_krw(self):
        krw = exchange_utils.get_krw()
        self.logger.debug(krw)

    def test_get_current_price(self):
        ticker = "COMP/KRW"
        current_price = exchange_utils.get_current_price(ticker)
        self.logger.debug(current_price)

    def test_get_avg_buy_price(self):
        ticker = "COMP/KRW"
        current_price = exchange_utils.get_avg_buy_price(ticker)
        self.logger.debug(current_price)
    
    def test_get_balance(self):
        ticker = "COMP/KRW"
        balance = exchange_utils.get_balance(ticker)
        self.logger.debug(balance)

    def test_create_sell_order(self):
        ticker = "COMP/KRW"
        balance = exchange_utils.get_balance(ticker)
        res = exchange_utils.create_sell_order(ticker, balance)
        self.logger.debug(res)

    def test_create_buy_order(self):
        ticker = "COMP/KRW"
        amount = 0.06
        res = exchange_utils.create_buy_order(ticker, amount)
        self.logger.debug(res)

    def test_get_candles(self):
        ticker = "COMP/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        self.logger.debug(candles)