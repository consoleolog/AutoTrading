import unittest
import time

import numpy as np
from scipy.optimize import curve_fit

from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from model.dto.ema import EMA
from model.dto.histogram import Histogram
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
    axes[1].bar(data.index, data[Histogram.UP], label="MACD Up Histogram", color="gray", alpha=0.5)
    axes[1].set_title("MACD Up")
    axes[1].legend()
    axes[1].grid(True)

    # MACD Mid, Low 그래프
    axes[2].plot(data[MACD.MID], label="MACD Mid", color="blue")
    axes[2].plot(data[MACD.MID_SIGNAL], label="MACD Mid Signal", color="orange")
    axes[2].bar(data.index, data[Histogram.MID], label="MACD Mid Histogram", color="gray", alpha=0.5)

    axes[2].plot(data[MACD.LOW], label="MACD Low", color="green")
    axes[2].plot(data[MACD.LOW_SIGNAL], label="MACD Low Signal", color="red")
    axes[2].bar(data.index, data[Histogram.LOW], label="MACD Low Histogram", color="purple", alpha=0.5)
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
        MACD Up  Histogram : {data[Histogram.UP].iloc[-2]}
        MACD Up  Gradient  : {data[MACD.UP_GRADIENT].iloc[-2]}
        
        MACD Mid           : {data[MACD.MID].iloc[-2]}
        MACD Mid Signal    : {data[MACD.MID_SIGNAL].iloc[-2]}
        MACD Mid Histogram : {data[Histogram.MID].iloc[-2]}
        MACD Mid Gradient  : {data[MACD.MID_GRADIENT].iloc[-2]}
        
        MACD Low           : {data[MACD.LOW].iloc[-2]}
        MACD Low Signal    : {data[MACD.LOW_SIGNAL].iloc[-2]}
        MACD Low Histogram : {data[Histogram.LOW].iloc[-2]}
        MACD Low Gradient  : {data[MACD.LOW_GRADIENT].iloc[-2]}
        """)

        mode, stage = data_utils.select_mode(data)
        self.logger.debug(mode)
        self.logger.debug(stage)

    def test_calculate_slope(self):
        ticker = "ETH/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        data = data_utils.create_sub_data(candles)

        macd_up, macd_mid, macd_low = data[MACD.UP], data[MACD.MID], data[MACD.LOW]
        #
        # # 두 지점 간 변화량 계산
        y_change = macd_up.iloc[-2] - macd_up.iloc[-3]
        x_change = 30

        # 기울기 계산 (단위: degrees)
        slope = (y_change / 500000000)

        self.logger.debug(f"Slope: {slope}")

        # rise = macd_up - macd_up.shift(1)
        # # 기울기 = rise / run
        # run = 6
        # slope = rise / run
        # self.logger.debug( slope)

    def test_calculate_time(self):
        current_time = time.time()

        # 5분(300초) 뺀 시간 계산
        five_minutes_ago = current_time - (5 * 60)

        # 결과 로그 출력
        self.logger.debug(f"현재 시간: {current_time}")
        self.logger.debug(f"5분 전 시간: {five_minutes_ago}")

    def test_curve_fit(self):
        current_time = time.time()
        ticker = "BTC/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        data = data_utils.create_sub_data(candles)

        def fnc(x, a, b, c):
            return a*x + b*x**2 + c
        opt, cov = curve_fit(fnc, data[MACD.UP].iloc[-3:], [300000000 * 3, 300000000 * 2, 300000000])
        self.logger.debug(opt)
        self.logger.debug(cov)
        a, b, c = opt
        self.logger.debug(f"a : {a}")
        self.logger.debug(f"b : {b}")
        self.logger.debug(f"c : {c}")


        x = np.array([300000000 * 3, 300000000 * 2, 300000000])
        plt.plot(x, fnc(x, a, b, c))
        plt.show()


    def test_show_graph(self):
        ticker = "BTC/KRW"
        candles = exchange_utils.get_candles(ticker, TimeFrame.MINUTE_5)
        data = data_utils.create_sub_data(candles)

        # plt.grid(b=True, color="DarkTurquoise", alpha=0.3, linestyle=":")
        #

