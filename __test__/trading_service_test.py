import unittest
import uuid
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mplfinance as mpf
from matplotlib.pyplot import ylabel
from scipy.signal import find_peaks
from ioc_container import IocContainer
from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from model.dto.ema import EMA
from model.dto.macd import MACD
from model.entity.candle import Candle
from repository.candle_repository import ICandleRepository
from repository.order_repository import IOrderRepository
from service.trading_service import ITradingService
from utils import exchange_utils, data_utils


class TradingServiceTest(unittest.TestCase):

    def setUp(self):
        self.container = IocContainer()
        self.container.compose()

        self.candle_repository = self.container.get(ICandleRepository)
        self.order_repository = self.container.get(IOrderRepository)
        self.trading_service = self.container.get(ITradingService)

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
        ticker = "SOL/KRW"
        profit = self.trading_service.calculate_profit(ticker)
        self.logger.info(profit)

    def test_bullish(self):
        ticker = "BTC/KRW"
        df = exchange_utils.get_candles(ticker, TimeFrame.HALF_HOUR)
        data = data_utils.create_sub_data(df).iloc[-5:]

        # 시간 인덱스 생성
        times = list(data.index)

        # 그래프 설정
        fig, axs = plt.subplots(4, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [4, 1, 1, 1]})

        # (1) 가격 + EMA 그래프
        axs[0].plot(times, data["close"], color="crimson", label="Close Price")
        axs[0].plot(times, data[EMA.SHORT], color="red", label="EMA Short")
        axs[0].plot(times, data[EMA.MID], color="orange", label="EMA Mid")
        axs[0].plot(times, data[EMA.LONG], color="blue", label="EMA Long")
        axs[0].legend()
        axs[0].set_title(f"{ticker} Price & EMA")
        axs[0].grid()

        # (2) MACD 그래프
        axs[1].plot(times, data[MACD.UP], color="blue", label="MACD")
        axs[1].plot(times, data[MACD.UP_SIGNAL], color="red", linestyle="dashed", label="Signal Line")
        axs[1].bar(times, data[MACD.UP_HISTOGRAM])
        axs[1].legend()
        axs[1].set_title("MACD (상)")
        axs[1].grid()

        # (2) MACD 그래프
        axs[2].plot(times, data[MACD.MID], color="blue", label="MACD")
        axs[2].plot(times, data[MACD.MID_SIGNAL], color="red", linestyle="dashed", label="Signal Line")

        axs[2].legend()
        axs[2].set_title("MACD (중)")
        axs[2].grid()

        axs[3].plot(times, data[MACD.LOW], color="blue", label="MACD")
        axs[3].plot(times, data[MACD.LOW_SIGNAL], color="red", linestyle="dashed", label="Signal Line")

        axs[3].legend()
        axs[3].set_title("MACD (하)")
        axs[3].grid()


        plt.tight_layout()
        plt.show()

    def test_mlp(self):
        ticker = "COMP/KRW"
        df = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_10)
        data = data_utils.create_sub_data(df)
        df_draw = data[-50:]

        adps = [
            mpf.make_addplot(df_draw[EMA.SHORT], panel=0, type="line"),
            mpf.make_addplot(df_draw[EMA.MID], panel=0, type="line"),
            mpf.make_addplot(df_draw[EMA.LONG], panel=0, type="line"),


            mpf.make_addplot(df_draw[MACD.UP], panel=1, type="line"),
            mpf.make_addplot(np.zeros((len(df_draw))), panel=1, type="line", color="red", linestyle='dotted',secondary_y=False),
            mpf.make_addplot(df_draw[MACD.UP_SIGNAL], panel=1, type='line', color='orange', secondary_y=False),
            mpf.make_addplot(df_draw[MACD.UP_HISTOGRAM], panel=1,type='bar', color='green',secondary_y=False),

            mpf.make_addplot(df_draw[MACD.MID], panel=2, type="line"),
            mpf.make_addplot(np.zeros((len(df_draw))), panel=2, type="line", color="red", linestyle='dotted',secondary_y=False),
            mpf.make_addplot(df_draw[MACD.MID_SIGNAL], panel=2, type='line', color='orange', secondary_y=False),
            mpf.make_addplot(df_draw[MACD.MID_HISTOGRAM], panel=2, type='bar', color='green', secondary_y=False),

            mpf.make_addplot(df_draw[MACD.LOW], panel=3, type="line"),
            mpf.make_addplot(np.zeros((len(df_draw))), panel=3, type="line", color="red", linestyle='dotted',secondary_y=False),
            mpf.make_addplot(df_draw[MACD.LOW_SIGNAL], panel=3, type='line', color='orange', secondary_y=False),
            mpf.make_addplot(df_draw[MACD.LOW_HISTOGRAM], panel=3, type='bar', color='green', secondary_y=False),

        ]

        fig, axs = mpf.plot(df_draw, style="charles", figratio=(3,2), figscale=3.3, addplot=adps, returnfig=True)
        mpf.show()

    def test_fast_trading(self):
        timeframe = TimeFrame.MINUTE_15
        ticker = "COMP/KRW"
        df = exchange_utils.get_candles(ticker, timeframe)

        df["EMA_HIGH"] = df["high"].ewm(span=10).mean()


