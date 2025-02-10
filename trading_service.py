import abc
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import exchange
import utils
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
    def calculate_profit(self, ticker):
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
            "BTC/KRW": 0.0001,
            "ETH/KRW": 0.0015,
            "BCH/KRW": 0.011,
            "AAVE/KRW": 0.015,
            "SOL/KRW": 0.02,
            "BSV/KRW": 0.1,
            "YFI/KRW": 0.0006,
            "BNB/KRW": 0.007,
            "COMP/KRW": 0.09,
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

    def calculate_profit(self, ticker):
        order_history = self.order_repository.find_by_ticker(ticker)
        current_price = exchange.get_current_price(ticker)
        buy_price = float(order_history["close"].iloc[-1])
        return (current_price - buy_price) / buy_price * 100.0

    def start_trading(self, timeframe: TimeFrame):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.auto_trading, ticker, timeframe) for ticker in self.ticker_list]
            result = [f.result() for f in futures]
        self.logger.info(result)

    def buy_condition(self, data):
        rsi = data[RSI.RSI]
        peekout, bullish = utils.peekout(data, "buy"), utils.bullish(data)
        return True if peekout and bullish and rsi.iloc[-2] <= 30 <= rsi.iloc[-1] else False
    def all_sell_condition(self, data):
        rsi = data[RSI.RSI]
        peekout, bearish = utils.peekout(data, "sell"), utils.bearish(data)
        return True if peekout and bearish and rsi.iloc[-1] >= 70 else False
    def half_sell_condition(self, data):
        rsi = data[RSI.RSI]
        peekout = utils.peekout(data, "sell")
        return True if peekout and rsi.iloc[-1] >= 70 else False

    def auto_trading(self, ticker:str, timeframe: TimeFrame):
        stage, data = utils.get_data(ticker, timeframe, 5, 8, 13)
        krw = exchange.get_krw()
        balance = exchange.get_balance(ticker)

        # BUY
        if balance == 0:
            candle = self.save_candle_data(ticker, timeframe, data, stage)
            if self.buy_condition(data) and krw > 8000 and (stage == 4 or stage == 5 or stage == 6):
                res = exchange.create_buy_order(ticker, self.price_keys[ticker])
                self.save_order_history(candle, res)
        # SELL
        else:
            if self.half_sell_condition(data) and ( stage == 1 or stage == 2 or stage == 3 ):
                candle = self.save_candle_data(ticker, timeframe, data, stage)
                res = exchange.create_sell_order(ticker, balance / 2)
                self.save_order_history(candle, res)
            elif self.all_sell_condition(data) and ( stage == 1 or stage == 2 or stage == 3 ):
                candle = self.save_candle_data(ticker, timeframe, data, stage)
                res = exchange.create_buy_order(ticker, balance)
                self.save_order_history(candle, res)
