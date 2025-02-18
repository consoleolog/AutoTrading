# -*- coding: utf-8 -*-
import abc
import os
import uuid
import pickle

import ccxt

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
    def calculate_profit(self, candle: Candle):
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

    def calculate_profit(self, candle: Candle):
        order_history = self.order_repository.find_by_ticker(candle.ticker)
        curr_price = candle.close
        buy_price = float(order_history["close"].iloc[-1])
        return ((curr_price - buy_price) / buy_price) * 100.0

    def start_trading(self, timeframe: TimeFrame):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.auto_trading, ticker, timeframe) for ticker in self.ticker_list]
            result = [f.result() for f in futures]
        self.logger.info(result)

    def auto_trading(self, ticker: str, timeframe: TimeFrame):
        info = {}
        stage, data = utils.get_data(ticker, timeframe, 5, 8, 13)
        balance = exchange.get_balance(ticker)
        rsi = data[RSI.LONG].iloc[-1]
        if balance == 0:
            bullish = data[MACD.SHORT_BULLISH].iloc[-2:].isin([True]).any()
            peekout = all([
                data[MACD.SHORT_HIST].iloc[-1] <= 0,
                data[MACD.LONG_HIST].iloc[-1] <= 0,
                data[MACD.SHORT_HIST].iloc[-1] > data[MACD.SHORT_HIST].iloc[-7:].min(),
                data[MACD.LONG_HIST].iloc[-1] > data[MACD.LONG_HIST].iloc[-7:].min(),
            ])
            if peekout and rsi <= 40 and stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.STABLE_INCREASE]:
                candle = Candle.of(str(uuid.uuid4()), datetime.now(), ticker, data["close"].iloc[-1],
                                   timeframe)
                res = exchange.create_buy_order(ticker, self.price_keys[ticker])
                order = Order.of(candle, res, datetime.now())
                self.order_repository.save(order)
            info["data"] = f"[MACD: {bullish} | RSI: {rsi}]"
        else:
            candle = Candle.of(str(uuid.uuid4()), datetime.now(), ticker, data["close"].iloc[-1],timeframe)
            profit = self.calculate_profit(candle)
            if profit > 0.1:
                res = exchange.create_sell_order(ticker, balance)
                order = Order.of(candle, res, datetime.now())
                self.order_repository.save(order)
            info["profit"] = f"[Profit: {profit}]"

        info["info"] = f"[Ticker: {ticker} | Stage: {stage}]"
        return info