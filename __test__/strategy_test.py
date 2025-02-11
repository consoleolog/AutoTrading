import unittest

import utils
from dto.stochastic import Stochastic
from logger import LoggerFactory
from constant.timeframe import TimeFrame
from dto.rsi import RSI


class StrategyTest(unittest.TestCase):

    def setUp(self):
        self.logger = LoggerFactory().get_logger(__class__.__name__)
        LoggerFactory.set_stream_level(LoggerFactory.DEBUG)

    def testGetData(self):
        ticker = "ETH/KRW"
        timeframe = TimeFrame.MINUTE_3
        stage, data = utils.get_data(ticker, timeframe)
        self.logger.debug(stage)
        self.logger.debug(data)
        self.logger.debug(data[Stochastic.D_SLOW].iloc[-1])
        self.logger.debug(data[Stochastic.D_FAST].iloc[-1])

    def test_trading(self):
        ticker = "BTC/KRW"
        timeframe = TimeFrame.MINUTE_3
        stage, data = utils.get_data(ticker, timeframe,5,8,13)
        rsi = data[RSI.RSI]
        self.logger.debug(stage)
        self.logger.debug(rsi.iloc[-1])
        peekout, rsi_cross = utils.peekout(data, "buy"), True if data[RSI.BULLISH].iloc[-2:].isin([True]).any() else False

        self.logger.debug(peekout)
        self.logger.debug(rsi_cross)
        # self.logger.debug(data[RSI.BULLISH].iloc[-5:])
        # if stage == 4 or stage == 5 or stage == 6:
        #     self.logger.debug("---- buy ----")
        #     peekout, bullish = utils.peekout(data, "buy"), utils.bullish(data)
        #
        #     self.logger.debug(peekout)
        #     self.logger.debug(bullish)
        #
        # elif stage == 1 or stage == 2 or stage == 3:
        #     peekout, bearish = utils.peekout(data, "sell"), utils.bearish(data)
        #
        #     self.logger.debug(peekout)
        #     self.logger.debug(bearish)
        #     if peekout and rsi >= 70:
        #         self.logger.debug("sell")

    def testStochastic(self):
        ticker = "BTC/KRW"
        timeframe = TimeFrame.MINUTE_3
        stage, data = utils.get_data(ticker, timeframe,5,8,13)

        d_fast = data[Stochastic.D_FAST].iloc[-1]
        d_slow = data[Stochastic.D_SLOW].iloc[-1]

        self.logger.debug(d_fast)
        self.logger.debug(d_slow)
