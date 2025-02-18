# -*- coding: utf-8 -*-
import abc
import exchange
import utils
from concurrent.futures import ThreadPoolExecutor
from dto.macd import MACD
from logger import LoggerFactory
from constant.stage import Stage
from constant.timeframe import TimeFrame
from dto.rsi import RSI
from repository.order_repository import IOrderRepository

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

class TradingService(ITradingService):
    def __init__(
            self,
            ticker_list,
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
        self.order_repository = order_repository

    def calculate_profit(self, ticker):
        orders = self.order_repository.find_by_ticker(ticker)
        buy_price = float(orders.iloc[-1]["price"])
        curr_price = exchange.get_current_price(ticker)
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
            if peekout and rsi <= 45 and stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.STABLE_INCREASE]:
                exchange.create_buy_order(ticker, self.price_keys[ticker])
                self.order_repository.save(ticker, exchange.get_current_price(ticker), "bid")
            info["data"] = f"[MACD: {bullish} | RSI: {rsi}]"
        else:
            profit = self.calculate_profit(ticker)
            if profit > 0.1:
                exchange.create_sell_order(ticker, balance)
                self.order_repository.save(ticker, exchange.get_current_price(ticker), "ask")
            info["profit"] = f"[Profit: {profit}]"
        info["info"] = f"[Ticker: {ticker} | Stage: {stage}]"
        return info