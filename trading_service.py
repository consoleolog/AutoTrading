# -*- coding: utf-8 -*-
import abc
import os
import uuid
import pickle
import exchange
import utils
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dto.macd import MACD
from dto.stochastic import Stochastic
from logger import LoggerFactory
from constant.stage import Stage
from constant.timeframe import TimeFrame
from dto.rsi import RSI
from entity.candle import Candle
from entity.candle_ema import CandleEMA
from entity.candle_macd import CandleMACD
from entity.order import Order
from repository.candle_repository import ICandleRepository
from repository.order_repository import IOrderRepository

class ITradingService(abc.ABC):
    @abc.abstractmethod
    def save_candle_data(self, ticker , timeframe: TimeFrame, data, stage: Stage)->Candle:
        pass
    @abc.abstractmethod
    def save_order_history(self, candle, response)->Order:
        pass
    @abc.abstractmethod
    def calculate_profit(self, ticker, buy_price):
        pass
    @abc.abstractmethod
    def start_trading(self, timeframe: TimeFrame):
        pass
    @abc.abstractmethod
    def auto_trading(self, ticker:str, timeframe: TimeFrame):
        pass

class TradingService(ITradingService):
    def __init__(
            self,
            ticker_list,
            candle_repository: ICandleRepository,
            order_repository: IOrderRepository,
    ):
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        LoggerFactory.set_stream_level(LoggerFactory.INFO)
        self.ticker_list = ticker_list
        self.price_keys = {
            "BTC/KRW": 0.0002,
            "ETH/KRW": 0.0090,
            "BCH/KRW": 0.022,
            "AAVE/KRW": 0.030,
            "SOL/KRW": 0.04,
            "ENS/KRW": 0.5,
        }
        self.candle_repository = candle_repository
        self.order_repository = order_repository

    def save_candle_data(self, ticker , timeframe: TimeFrame, data, stage: Stage)->Candle:
        try:
            candle = self.candle_repository.save_candle(
                Candle.of(str(uuid.uuid4()), datetime.now(), ticker, data["close"].iloc[-1], timeframe))
            candle_ema = self.candle_repository.save_candle_ema(CandleEMA.of(candle.candle_id, stage, data))
            self.candle_repository.save_candle_macd(CandleMACD.of(candle_ema.candle_id, data))
            return candle
        except Exception as e:
            self.logger.warning(e.__traceback__)
            pass
    def save_order_history(self, candle, response)-> Order:
        try:
            order = Order.of(candle, response, datetime.now())
            self.order_repository.save(order)
            return order
        except Exception as e:
            self.logger.warning(e.__traceback__)
            pass

    def calculate_profit(self, ticker, buy_price):
        current_price = exchange.get_current_price(ticker)
        return (current_price - buy_price) / buy_price * 100.0

    def start_trading(self, timeframe: TimeFrame):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.auto_trading, ticker, timeframe) for ticker in self.ticker_list]
            result = [f.result() for f in futures]
        self.logger.info(result)

    def auto_trading(self, ticker: str, timeframe: TimeFrame):
        stage, data = utils.get_data(ticker, timeframe, 5, 8, 13)
        balance = exchange.get_balance(ticker)

        info = utils.load_info()
        if ticker not in info:
            info[ticker] = {"position": "long", "stoch": False, "macd": False, "rsi": False}

        MACD_BULLISH = all([
            data[MACD.SHORT_BULLISH].iloc[-3:].isin([True]).any(),
            data[MACD.LONG_BULLISH].iloc[-2:].isin([True]).any(),
        ])
        MACD_BEARISH = all([
            data[MACD.SHORT_BEARISH].iloc[-3:].isin([True]).any(),
            data[MACD.LONG_BEARISH].iloc[-2:].isin([True]).any(),
        ])
        # BUY
        if balance == 0:
            info[ticker]["position"] = "long"
            if "price" in info[ticker]:
                del info[ticker]["price"]

            if info[ticker]["position"] == "long":
                fast, slow = data[Stochastic.D_FAST].iloc[-1], data[Stochastic.D_SLOW].iloc[-1]
                # -*- 오신호 방지용 신호 초기화 조건 -*-
                if fast >= Stochastic.OVER_BOUGHT or slow >= Stochastic.OVER_BOUGHT:
                    # K 선이 과매수 상태 ( 75 이상 ) 에 있으면 모든 신호 초기화
                    info[ticker]["rsi"] = False
                    info[ticker]["macd"] = False
                    info[ticker]["stoch"] = False
                if data[MACD.SHORT_BEARISH].iloc[-3:-1].isin([True]).any():
                    # MACD 의 시그널이 하향 교차가 되면 모든 신호 초기화
                    info[ticker]["rsi"] = False
                    info[ticker]["macd"] = False
                    info[ticker]["stoch"] = False
                # -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-

                if fast <= Stochastic.OVER_SOLD or slow <= Stochastic.OVER_SOLD:
                    # K 선과 D 선이 과매도 상태에 있을 때 ( 25 이하 일 때)
                    info[ticker]["stoch"] = True

                if info[ticker]["stoch"]:
                    # Stochastic 의 신호를 만족하면서 MACD 의 시그널이 상향으로 교차했을 때
                    if MACD_BULLISH:
                        info[ticker]["macd"] = True

                    rsi, rsi_sig = data[RSI.LONG].iloc[-1], data[RSI.LONG_SIG].iloc[-1]
                    # Stochastic 의 신호와 MACD의 신호를 만족하면서 RSI 의 값이 50 이상 ( 시그널의 값보다 RSI 의 값이 커야함 (상승의 표시) )
                    if info[ticker]["macd"] and rsi >= 50 and rsi > rsi_sig:
                        info[ticker]["rsi"] = True

                    # Stochastic 신호와 MACD, RSI 의 조건을 만족하면 매수
                    if info[ticker]["macd"] and info[ticker]["rsi"]:
                        curr_price = data["close"].iloc[-2:].min()
                        info[ticker]["position"] = "short"
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        info[ticker]["price"] = float(curr_price)
                        if "profit" in info[ticker]:
                            del info[ticker]["profit"]
                        exchange.create_buy_order(ticker, self.price_keys[ticker])
        # SELL
        else:
            info[ticker]["position"] = "short"
            if "price" not in info[ticker]:
                info[ticker]["price"] = data["close"].iloc[-2:].min()

            if info[ticker]["position"] == "short":

                fast, slow = data[Stochastic.D_FAST].iloc[-1], data[Stochastic.D_SLOW].iloc[-1]
                # -*- 오신호 방지용 신호 초기화 조건 -*-
                if fast <= Stochastic.OVER_SOLD or slow <= Stochastic.OVER_SOLD:
                    # K 선이 과매도 상태 ( 25 이하 ) 면 모든 신호 초기화
                    info[ticker]["rsi"] = False
                    info[ticker]["macd"] = False
                    info[ticker]["stoch"] = False
                if MACD_BULLISH:
                    # MACD 의 시그널이 상향 교차하면 모든 신호 초기회
                    info[ticker]["rsi"] = False
                    info[ticker]["macd"] = False
                    info[ticker]["stoch"] = False
                # -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-

                if fast >= Stochastic.OVER_BOUGHT or slow >= Stochastic.OVER_BOUGHT:
                    # K 선과 D 선이 과매수 상태 일 때 ( 75 이상 일 때)
                    info[ticker]["stoch"] = True

                if info[ticker]["stoch"]:
                    # Stochastic 신호를 만족하면서 MACD 의 시그널이 하향 교차 했을 때
                    if MACD_BEARISH:
                        info[ticker]["macd"] = True

                    rsi, rsi_sig = data[RSI.LONG].iloc[-1], data[RSI.LONG_SIG].iloc[-1]
                    # Stochastic 신호와 MACD의 신호를 만족하면서 갔다가 RSI 가 50 이하 일 때
                    if info[ticker]["macd"] and rsi <= 50 and rsi < rsi_sig:
                        info[ticker]["rsi"] = True

                    if info[ticker]["macd"] and info[ticker]["rsi"]:
                        # Stochastic 신호와 MACD, RSI 의 조건을 만족하면 손절
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        exchange.create_sell_order(ticker, balance)

            profit = self.calculate_profit(ticker, info[ticker]["price"])
            info[ticker]["profit"] = profit
            # 수익이 0.2 가 넘으면 익절
            if profit >= 0.2:
                info[ticker]["position"] = "long"
                info[ticker]["stoch"] = False
                info[ticker]["macd"] = False
                info[ticker]["rsi"] = False
                exchange.create_sell_order(ticker, balance)
            # Stochastic 이 우하향했을 때 수익이 0.1 이 넘는다면 익절
            if profit >= 0.1 and data[Stochastic.BEARISH].iloc[-3:-1].isin([True]).any():
                info[ticker]["position"] = "long"
                info[ticker]["stoch"] = False
                info[ticker]["macd"] = False
                info[ticker]["rsi"] = False
                exchange.create_sell_order(ticker, balance)
        utils.save_info(info)
        info[ticker]["info"] = f"[Ticker: {ticker} | Stage: {stage}]"
        return info[ticker]
