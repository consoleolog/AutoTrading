import unittest

import exchange
from logger import LoggerFactory


class ExchangeTest(unittest.TestCase):
    def setUp(self):
        self.logger = LoggerFactory().get_logger(__class__.__name__)

    def testCreateBuyOrder(self):
        ticker = "AAVE/KRW"
        amount = 0.020

        res = exchange.create_buy_order(ticker, amount)
        self.logger.info(res)
    
    def testCreateSellOrder(self):
        ticker = "AAVE/KRW"
        amount = exchange.get_balance(ticker)
        res = exchange.create_sell_order(ticker, amount)
        self.logger.info(res)

