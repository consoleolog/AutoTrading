import unittest
from ioc_container import IocContainer
from logger import LoggerFactory
from constant import TimeFrame
from repository.candle_repository import ICandleRepository

class CandleRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.container = IocContainer()
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        self.candle_repository = self.container.get(ICandleRepository)

    def test_find_all_by_ticker(self):
        ticker = "BTC/KRW"
        data = self.candle_repository.find_all_by_ticker(ticker)
        self.logger.debug(data)

    def test_find_all_by_ticker_and_timeframe(self):
        ticker = "BTC/KRW"
        timeframe = TimeFrame.MINUTE_5
        data = self.candle_repository.find_all_by_ticker_and_timeframe(ticker, timeframe)
        self.logger.debug(data)