import unittest
import uuid
from datetime import datetime

from di_container import DIContainer
from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from model.entity.candle import Candle
from repository.candle_repository import CandleRepository
from repository.order_repository import OrderRepository
from service.trading_service import TradingService
from utils import exchange_utils, data_utils


class TradingServiceTest(unittest.TestCase):

    def setUp(self):
        self.container = DIContainer()
        self.container.compose()

        self.candle_repository = self.container.get(CandleRepository)
        self.order_repository = self.container.get(OrderRepository)
        self.trading_service = self.container.get(TradingService)

        self.logger = LoggerFactory().get_logger(__class__.__name__)

    def test_create_buy_order(self):
        ticker = "COMP/KRW"
        df = exchange_utils.get_candles(ticker, TimeFrame.HOUR)
        data = data_utils.create_sub_data(df)
        amount = 0.08
        res = exchange_utils.create_buy_order(ticker, amount)
        self.logger.debug(res)
        candle = Candle.of(str(uuid.uuid4()), datetime.now(), ticker, data["close"].iloc[-1], TimeFrame.HOUR)
        self.trading_service.save_order_history(candle, res)

    def test_create_sell_order(self):
        ticker = "COMP/KRW"
        df = exchange_utils.get_candles(ticker, TimeFrame.HOUR)
        data = data_utils.create_sub_data(df)
        balance = exchange_utils.get_balance(ticker)
        res = exchange_utils.create_sell_order(ticker, balance)
        self.logger.debug(res)
        candle = Candle.of(str(uuid.uuid4()), datetime.now(), ticker, data["close"].iloc[-1], TimeFrame.HOUR)
        self.trading_service.save_order_history(candle, res)

    def test_calculate(self):
        ticker = "COMP/KRW"
        profit = self.trading_service.calculate_profit(ticker)
        self.logger.info(profit)