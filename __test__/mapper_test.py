import unittest

from mappers import ticker_position_mapper, ticker_status_mapper


class MapperTest(unittest.TestCase):
    def setUp(self):
        self.ticker_position_mapper = ticker_position_mapper
        self.ticker_status_mapper = ticker_status_mapper

    def testFindByTickerForTickerStatus(self):
        ticker = "BTC/KRW"
        ticker_status = self.ticker_status_mapper.find_by_ticker(ticker)
        print(ticker_status.ticker)
        print(ticker_status.price)
        print(ticker_status.side)
        print(ticker_status.created_at)
        print(ticker_status.updated_at)

    def testInitForTickerPosition(self):
        tickers = [
            "BTC/KRW",
            "ETH/KRW",
            "BCH/KRW",
            "ENS/KRW",
            "SOL/KRW",
        ]
        for ticker in tickers:
            self.ticker_position_mapper.init(ticker)
    def testRefresh(self):
        tickers = [
            "BTC/KRW",
            "ETH/KRW",
            "BCH/KRW",
            "ENS/KRW",
            "SOL/KRW",
        ]
        for ticker in tickers:
            self.ticker_position_mapper.refresh(ticker)