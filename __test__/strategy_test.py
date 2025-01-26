import unittest
import time

import numpy as np
from scipy.optimize import curve_fit

from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from model.dto.ema import EMA
from model.dto.macd import MACD
from utils import exchange_utils, data_utils
import matplotlib.pyplot as plt

def plot_create_sub_data(data):
    data = data.iloc[-20:]
    fig, axes = plt.subplots(3, 1, figsize=(12, 12), sharex=True)

    # EMA (Exponential Moving Averages) 그래프
    axes[0].plot(data[EMA.SHORT], label="EMA Short", color="blue")
    axes[0].plot(data[EMA.MID], label="EMA Mid", color="orange")
    axes[0].plot(data[EMA.LONG], label="EMA Long", color="green")
    axes[0].set_title("EMA (Exponential Moving Averages)")
    axes[0].legend()
    axes[0].grid(True)

    # MACD 그래프
    axes[1].plot(data[MACD.UP], label="MACD Up", color="blue")
    axes[1].plot(data[MACD.UP_SIGNAL], label="MACD Up Signal", color="orange")
    axes[1].bar(data.index, data[MACD.UP_HISTOGRAM], label="MACD Up Histogram", color="gray", alpha=0.5)
    axes[1].set_title("MACD Up")
    axes[1].legend()
    axes[1].grid(True)

    # MACD Mid, Low 그래프
    axes[2].plot(data[MACD.MID], label="MACD Mid", color="blue")
    axes[2].plot(data[MACD.MID_SIGNAL], label="MACD Mid Signal", color="orange")
    axes[2].bar(data.index, data[MACD.MID_HISTOGRAM], label="MACD Mid Histogram", color="gray", alpha=0.5)

    axes[2].plot(data[MACD.LOW], label="MACD Low", color="green")
    axes[2].plot(data[MACD.LOW_SIGNAL], label="MACD Low Signal", color="red")
    axes[2].bar(data.index, data[MACD.LOW_HISTOGRAM], label="MACD Low Histogram", color="purple", alpha=0.5)
    axes[2].set_title("MACD Mid & Low")
    axes[2].legend()
    axes[2].grid(True)

    # 그래프 공통 설정
    plt.xlabel("Timestamp")
    fig.tight_layout()
    plt.show()

def is_peekout():
    pass

class StrategyTest(unittest.TestCase):
    def setUp(self):
        self.logger = LoggerFactory.get_logger(__class__.__name__)
        LoggerFactory.set_stream_level(LoggerFactory.DEBUG)


    def test_create_sub_data(self):
        ticker = "BTC/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        data = data_utils.create_sub_data(candles)

        self.logger.debug(f"""
        EMA Short : {data[EMA.SHORT].iloc[-2]}
        EMA Mid   : {data[EMA.MID].iloc[-2]}
        EMA Long  : {data[EMA.LONG].iloc[-2]}
        Stage     : {EMA.get_stage(data)}
        
        MACD Up            : {data[MACD.UP].iloc[-2]}
        MACD Up  Signal    : {data[MACD.UP_SIGNAL].iloc[-2]}
        MACD Up  Histogram : {data[MACD.UP_HISTOGRAM].iloc[-2]}
        MACD Up  Gradient  : {data[MACD.UP_GRADIENT].iloc[-2]}
        
        MACD Mid           : {data[MACD.MID].iloc[-2]}
        MACD Mid Signal    : {data[MACD.MID_SIGNAL].iloc[-2]}
        MACD Mid Histogram : {data[MACD.MID_HISTOGRAM].iloc[-2]}
        MACD Mid Gradient  : {data[MACD.MID_GRADIENT].iloc[-2]}
        
        MACD Low           : {data[MACD.LOW].iloc[-2]}
        MACD Low Signal    : {data[MACD.LOW_SIGNAL].iloc[-2]}
        MACD Low Histogram : {data[MACD.LOW_HISTOGRAM].iloc[-2]}
        MACD Low Gradient  : {data[MACD.LOW_GRADIENT].iloc[-2]}
        """)

        mode, stage = data_utils.select_mode(data)
        self.logger.debug(mode)
        self.logger.debug(stage)

    def test_calculate_slope(self):
        ticker = "ETH/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        data = data_utils.create_sub_data(candles)
        # data["MACD_CROSSOVER"] = np.where(
        # (data[MACD.UP].shift(1) < data[MACD.UP_SIGNAL].shift(1)) & (data[MACD.UP] > data[MACD.UP_SIGNAL]), 'Bullish',
        # np.where(
        #     (data[MACD.UP].shift(1) > data[MACD.UP_SIGNAL].shift(1)) & (data[MACD.UP] < data[MACD.UP_SIGNAL]), 'Bearish',
        #     None
        #     )
        # )
        # crossovers = data[data['MACD_CROSSOVER'].notnull()]
        # self.logger.debug(crossovers[[MACD.UP, MACD.UP_SIGNAL, 'MACD_CROSSOVER']])
        self.logger.debug(data[MACD.UP_CROSSOVER])
        self.logger.debug(data[MACD.MID_CROSSOVER])
        self.logger.debug(data[MACD.LOW_CROSSOVER])


    def test_calculate_time(self):
        current_time = time.time()

        five_minutes_ago = current_time - (5 * 60)

        # 결과 로그 출력
        self.logger.debug(f"현재 시간: {current_time}")
        self.logger.debug(f"5분 전 시간: {five_minutes_ago}")


    def test_show_graph(self):
        ticker = "BTC/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        data = data_utils.create_sub_data(candles)

        # plt.grid(b=True, color="DarkTurquoise", alpha=0.3, linestyle=":")
        #

