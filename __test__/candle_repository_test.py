import unittest

import pandas as pd

from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from repository.candle_repository import CandleRepository
from utils.database import connection, engine


class CandleRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.connection = connection
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        self.candle_repository = CandleRepository(connection, engine)

    # def test_call_function(self):
    #     with self.connection.cursor() as cursor:
    #         cursor.execute("""
    #         SELECT * FROM public.get_candles();
    #         """)
    #         candles = cursor.fetchall()
    #         self.logger.debug(candles)

    def test_call_function_with_pd(self):
        sql = """
        SELECT * FROM public.get_candles();
        """

        data = pd.read_sql(sql, engine)
        self.logger.debug(data)

    def test_find_all_by_ticker(self):
        ticker = "BTC/KRW"
        data = self.candle_repository.find_all_by_ticker(ticker)
        self.logger.debug(data)

    def test_find_all_by_ticker_and_timeframe(self):
        ticker = "BTC/KRW"
        timeframe = TimeFrame.MINUTE_5
        data = self.candle_repository.find_all_by_ticker_and_timeframe(ticker, timeframe)
        self.logger.debug(data)