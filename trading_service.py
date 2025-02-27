# -*- coding: utf-8 -*-
import abc
import exchange
import utils
from concurrent.futures import ThreadPoolExecutor
from dto.macd import MACD
from dto.stochastic import Stochastic
from logger import LoggerFactory
from constant.stage import Stage
from constant.timeframe import TimeFrame
from dto.rsi import RSI
from repository.status_repository import IStatusRepository


class ITradingService(abc.ABC):
    @abc.abstractmethod
    def calculate_profit(self, ticker:str):
        pass
    @abc.abstractmethod
    def start_trading(self, timeframe: TimeFrame):
        pass
    @abc.abstractmethod
    def auto_trading(self, ticker:str, timeframe: TimeFrame):
        pass
    @abc.abstractmethod
    def init_status(self):
        pass

class TradingService(ITradingService):
    def __init__(
            self,
            ticker_list,
            status_repository: IStatusRepository,
    ):
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        LoggerFactory.set_stream_level(LoggerFactory.INFO)
        self.ticker_list = ticker_list
        self.price_keys = {
            "BTC/KRW": 0.0002,
            "ETH/KRW": 0.0090,
            "BCH/KRW": 0.044,
            "AAVE/KRW": 0.030,
            "SOL/KRW": 0.08,
            "ENS/KRW": 1,
        }
        self.status_repository = status_repository

    def init_status(self):
        for ticker in self.ticker_list:
            self.status_repository.save(ticker)

    def calculate_profit(self, ticker):
        status = self.status_repository.find_by_ticker(ticker)
        buy_price = float(status["price"])
        curr_price = exchange.get_current_price(ticker)
        return ((curr_price - buy_price) / buy_price) * 100.0

    def start_trading(self, timeframe: TimeFrame):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.auto_trading, ticker, timeframe) for ticker in self.ticker_list]
            result = [f.result() for f in futures]
        self.logger.info(result)

    def update_status(self, ticker):
        status = self.status_repository.find_by_ticker(ticker)
        if status["side"] == "bid":
            price = (float(status["price"]) + exchange.get_current_price(ticker)) / 2
            self.status_repository.update_one(ticker, price, "bid")
        else:
            self.status_repository.update_one(ticker, exchange.get_current_price(ticker), "bid")

    def auto_trading(self, ticker: str, timeframe: TimeFrame):
        info = {}
        stage, data = utils.get_data(ticker, timeframe, 5, 8, 13)
        balance = exchange.get_balance(ticker)
        rsi = data[RSI.LONG].iloc[-1]
        bullish = data[MACD.SHORT_BULLISH].iloc[-2:].isin([True]).any() or data[MACD.LONG_BULLISH].iloc[-2:].isin([True]).any()
        peekout = all([
            data[MACD.SHORT_HIST].iloc[-1] > data[MACD.SHORT_HIST].iloc[-7:].min(),
            data[MACD.LONG_HIST].iloc[-1] > data[MACD.LONG_HIST].iloc[-7:].min(),
        ])
        if bullish and peekout and rsi <= 40 and exchange.get_krw() > 40000 and stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.START_OF_INCREASE]:
            self.update_status(ticker)
            exchange.create_buy_order(ticker, self.price_keys[ticker])
        info["data"] = f"[MACD: {bullish} | RSI: {rsi}]"
        if balance != 0:
            stoch_bearish = data[Stochastic.BEARISH].iloc[-2:].isin([True]).any()
            profit = self.calculate_profit(ticker)
            if profit < 0 and stoch_bearish and stage == Stage.STABLE_INCREASE:
                exchange.create_sell_order(ticker, balance)
                self.status_repository.update_one(ticker, exchange.get_current_price(ticker), "ask")

            if profit > 0.1 and stoch_bearish and stage in [Stage.STABLE_INCREASE, Stage.END_OF_INCREASE, Stage.START_OF_DECREASE]:
                exchange.create_sell_order(ticker, balance)
                self.status_repository.update_one(ticker, exchange.get_current_price(ticker), "ask")
            info["profit"] = f"[Profit: {profit}]"
        info["info"] = f"[Ticker: {ticker} | Stage: {stage}]"
        return info