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
            "BTC/KRW": 0.0002,
            "ETH/KRW": 0.0030,
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

    def auto_trading(self, ticker: str, timeframe: TimeFrame):
        stage, data = utils.get_data(ticker, timeframe, 5, 8, 13)
        balance = exchange.get_balance(ticker)
        with open(f"{os.getcwd()}/info.plk", "rb") as f:
            info = pickle.load(f)

        # BUY
        if balance == 0:
            info[ticker]["position"] = "long"
            with open(f"{os.getcwd()}/info.plk", "wb") as f:
                pickle.dump(info, f)

            rsi = data[RSI.RSI]
            if info[ticker]["position"] == "long" and stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.START_OF_INCREASE]:
                fast, slow = data[Stochastic.D_FAST], data[Stochastic.D_SLOW]
                if info[ticker]["stoch"] == False and fast.iloc[-1] < 25 and slow.iloc[-1] < 25 and rsi.iloc[-1] < 45:
                    info[ticker]["stoch"] = True
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)

                macd_bullish = True if data[MACD.BULLISH].iloc[:-2].isin([True]).any() else False
                if info[ticker]["stoch"] and macd_bullish:
                    info[ticker]["macd"] = True
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)

                if info[ticker]["stoch"] and info[ticker]["macd"] and rsi.iloc[-1] >= 50:
                    info[ticker]["rsi"] = True
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)

                if info[ticker]["stoch"] and info[ticker]["macd"] and info[ticker]["rsi"]:
                    if fast.iloc[-1] < 65:
                        info[ticker]["position"] = "short"
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        with open(f"{os.getcwd()}/info.plk", "wb") as f:
                            pickle.dump(info, f)
                        exchange.create_buy_order(ticker, self.price_keys[ticker])
                    else:
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        with open(f"{os.getcwd()}/info.plk", "wb") as f:
                            pickle.dump(info, f)
        # SELL
        else:
            info[ticker]["position"] = "short"
            with open(f"{os.getcwd()}/info.plk", "wb") as f:
                pickle.dump(info, f)

            if info[ticker]["position"] == "short":
                prev_low = data["low"].iloc[-2:].min()
                take_profit = prev_low * 1.5
                if data["close"].iloc[-1] >= take_profit:
                    info[ticker]["position"] = "long"
                    info[ticker]["stoch"] = False
                    info[ticker]["macd"] = False
                    info[ticker]["rsi"] = False
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)
                    exchange.create_sell_order(ticker, balance)

                if data[Stochastic.BEARISH].iloc[-2:].isin([True]).any():
                    exchange.create_sell_order(ticker, balance / 2)

                fast, slow = data[Stochastic.D_FAST], data[Stochastic.D_SLOW]
                rsi = data[RSI.RSI]

                if info[ticker]["stoch"] == False and fast.iloc[-1] > 70 and slow.iloc[-1] > 70 and rsi.iloc[-1] > 55:
                    info[ticker]["stoch"] = True
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)

                macd_bearish = True if data[MACD.BEARISH].iloc[:-2].isin([True]).any() else False
                if info[ticker]["stoch"] and macd_bearish:
                    info[ticker]["macd"] = True
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)

                if info[ticker]["stoch"] and info[ticker]["macd"] and rsi.iloc[-1] < 55:
                    info[ticker]["rsi"] = True
                    with open(f"{os.getcwd()}/info.plk", "wb") as f:
                        pickle.dump(info, f)

                if info[ticker]["stoch"] and info[ticker]["macd"] and info[ticker]["rsi"] :
                    if rsi.iloc[-1] > 25:
                        info[ticker]["position"] = "long"
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        with open(f"{os.getcwd()}/info.plk", "wb") as f:
                            pickle.dump(info, f)
                        exchange.create_sell_order(ticker, balance)
                    else:
                        info[ticker]["stoch"] = False
                        info[ticker]["macd"] = False
                        info[ticker]["rsi"] = False
                        with open(f"{os.getcwd()}/info.plk", "wb") as f:
                            pickle.dump(info, f)

        info[ticker]["ticker"] = ticker
        return info[ticker]