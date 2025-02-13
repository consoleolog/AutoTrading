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
    def __init__(self,
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
        with open(f"{os.getcwd()}/info.plk", "rb") as f:
            info = pickle.load(f)

        # BUY
        if balance == 0:
            info[ticker]["position"] = "long"
            if "price" in info[ticker]:
                del info[ticker]["price"]

            if info[ticker]["position"] == "long" and stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.START_OF_INCREASE]:

                # -*- 오신호 방지용 신호 초기화 조건들 -*-
                if data[MACD.BEARISH].iloc[-2:].isin([True]).any():
                    # MACD 의 시그널이 하향 교차가 되면 MACD 의 신호를 초기화
                    info[ticker]["macd"] = False
                if data[RSI.BEARISH].iloc[-2:].isin([True]).any():
                    # RSI 의 시그널이 하향 교차가 되면 RSI 의 신호를 초기화
                    info[ticker]["rsi"] = False
                if data[Stochastic.BEARISH].iloc[-2:].isin([True]).any():
                    # K 선이 D 선을 하향 교차 했으면 Stochastic 의 신호를 초기화
                    info[ticker]["stoch"] = False
                # -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-

                fast, slow = data[Stochastic.D_FAST].iloc[-1], data[Stochastic.D_SLOW].iloc[-1]
                if fast <= 30 and slow <= 30:
                    # K 선과 D 선이 과매도 상태에 있을 때 ( 30 이하 일 때)
                    info[ticker]["stoch"] = True

                macd, macd_sig = data[MACD.MACD].iloc[-1], data[MACD.SIG].iloc[-1]
                if info[ticker]["stoch"] and data[MACD.BULLISH].iloc[-2:].isin([True]).any() and macd > macd_sig:
                    # Stochastic 의 신호를 만족하면서 MACD 의 시그널이 상향으로 교차했을 때
                    info[ticker]["macd"] = True

                rsi, rsi_sig = data[RSI.RSI].iloc[-1], data[RSI.SIG].iloc[-1]
                if info[ticker]["stoch"] and rsi >= 50 and rsi > rsi_sig:
                    # Stochastic 의 신호를 만족하면서 RSI 의 값이 50 이상 ( 시그널의 값보다 RSI 의 값이 커야함 (상승의 표시) )
                    info[ticker]["rsi"] = True

                if info[ticker]["stoch"] and info[ticker]["macd"] and info[ticker]["rsi"]:
                    # Stochastic 신호와 MACD, RSI 의 조건을 만족하면 매수 검토
                    # 만약 K 선이 과매수 상태에 들어서지 않았다면 매수 진행
                    if fast <= 70:
                        curr_price = data["close"].iloc[-1]
                        info[ticker]["position"] = "short"
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        info[ticker]["price"] = float(curr_price)
                        exchange.create_buy_order(ticker, self.price_keys[ticker])
                    # K 선이 과매수 상태 라면 이전 신호들을 모두 초기화
                    else:
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                # 변경 사항 저장
                with open(f"{os.getcwd()}/info.plk", "wb") as f:
                    pickle.dump(info, f)
        # SELL
        else:
            info[ticker]["position"] = "short"
            if "price" not in info[ticker]:
                info[ticker]["price"] = data["close"].iloc[-2:].min()

            with open(f"{os.getcwd()}/info.plk", "wb") as f:
                pickle.dump(info, f)

            if info[ticker]["position"] == "short":
                # 수익이 0.5 가 넘으면 익절
                profit = self.calculate_profit(ticker, info[ticker]["price"])
                if profit > 0.5:
                    info[ticker]["position"] = "long"
                    info[ticker]["stoch"] = False
                    info[ticker]["macd"] = False
                    info[ticker]["rsi"] = False
                    if "price" in info[ticker]:
                        del info[ticker]["price"]
                    exchange.create_sell_order(ticker, balance)

                # -*- 오신호 방지용 신호 초기화 조건들 -*-
                if data[MACD.BULLISH].iloc[-2:].isin([True]).any():
                    # MACD 의 시그널이 상향 교차하면 MACD 신호 초기화
                    info[ticker]["macd"] = False
                if data[RSI.BULLISH].iloc[-2:].isin([True]).any():
                    # RSI 의 시그널이 상향 교차하면 RSI 신호 초기화
                    info[ticker]["rsi"] = False
                if data[Stochastic.BULLISH].iloc[-2:].isin([True]).any():
                    # K 선이 D 선을 상향 교차하면 Stochastic 의 신호를 초기화
                    info[ticker]["stoch"] = False
                # -*- -*- -*- -*- -*- -*- -*- -*- -*- -*-

                fast, slow = data[Stochastic.D_FAST].iloc[-1], data[Stochastic.D_SLOW].iloc[-1]
                if info[ticker]["stoch"] == False and fast >= 70 and slow >= 70:
                    # K 선과 D 선이 과매수 상태 일 때 ( 70 이상 일 때)
                    info[ticker]["stoch"] = True

                macd, macd_sig = data[MACD.MACD].iloc[-1], data[MACD.SIG].iloc[-1]
                if info[ticker]["stoch"] and data[MACD.BEARISH].iloc[-2:].isin([True]).any() and macd < macd_sig:
                    # Stochastic 신호를 만족하면서 MACD 의 시그널이 하향 교차 했을 때
                    info[ticker]["macd"] = True

                rsi, rsi_sig = data[RSI.RSI].iloc[-1], data[RSI.SIG].iloc[-1]
                if info[ticker]["stoch"] and rsi <= 50 and rsi < rsi_sig:
                    # Stochastic 신호를 만족하면서 갔다가 RSI 가 50 이하 일 때
                    info[ticker]["rsi"] = True

                if info[ticker]["stoch"] and info[ticker]["macd"] and info[ticker]["rsi"]:
                    # Stochastic 신호와 MACD, RSI 의 조건을 만족하면 손절 검토
                    # 만약 K 선이 과매도 상태에 들어서지 않았다면 손절
                    if fast >= 30:
                        info[ticker]["position"] = "long"
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        if "price" in info[ticker]:
                            del info[ticker]["price"]
                        exchange.create_sell_order(ticker, balance)
                    # K 선이 과매도 상태라면 이전 신호들을 모두 초기화
                    else:
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                # 변경사항 반영
                with open(f"{os.getcwd()}/info.plk", "wb") as f:
                    pickle.dump(info, f)

        info[ticker]["ticker"] = ticker
        return info[ticker]
