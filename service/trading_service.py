import abc
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pandas import DataFrame
from logger import LoggerFactory
from model.const.stage import Stage
from model.const.timeframe import TimeFrame
from model.dto.ema import EMA
from model.dto.macd import MACD
from model.entity.candle import Candle
from model.entity.candle_ema import CandleEMA
from model.entity.candle_macd import CandleMACD
from model.entity.order import Order
from repository.candle_repository import ICandleRepository
from repository.order_repository import IOrderRepository
from utils import exchange_utils, data_utils

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
    @abc.abstractmethod
    def _print_trading_report(self, ticker: str, data: DataFrame):
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
        current_price = exchange_utils.get_current_price(ticker)
        buy_price = float(order_history["close"].iloc[-1])
        return (current_price - buy_price) / buy_price * 100.0

    def start_trading(self, timeframe: TimeFrame):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.auto_trading, ticker, timeframe) for ticker in self.ticker_list]
            result = [f.result() for f in futures]
        self.logger.info(result)

    def auto_trading(self, ticker:str, timeframe: TimeFrame):
        result = {"ticker": ticker}
        candles = exchange_utils.get_candles(ticker, timeframe)
        data = data_utils.create_sub_data(candles)
        mode, stage = data_utils.select_mode(data)
        candle = self.save_candle_data(ticker, timeframe, data, stage)
        krw = exchange_utils.get_krw()
        balance = exchange_utils.get_balance(ticker)

        # Check Peekout of Histogram
        peekout = data_utils.peekout(data, mode)

        # BUY
        if balance == 0 and mode == "buy" and peekout and krw > 8000:
            # Check Cross Signal
            bullish = True if data[MACD.UP_CROSSOVER].iloc[-2:].isin([MACD.UP_BULLISH]).any() else False
            result["result"] = f"Bullish: {bullish}"
            if bullish:
                response = exchange_utils.create_buy_order(ticker, self.price_keys[ticker])
                self.save_order_history(candle, response)
        # SELL
        elif balance != 0 and mode == "sell" and peekout:
            # Check Cross Signal
            bearish = True if data[MACD.UP_CROSSOVER].iloc[-2:].isin([MACD.UP_BEARISH]).any() else False
            result["result"] = f"Bearish: {bearish}"
            if bearish:
                response = exchange_utils.create_sell_order(ticker, balance)
                self.save_order_history(candle, response)

        result["info"] = f"Mode:{mode} Stage:{stage} Peekout: {peekout}"
        return result

    def _print_trading_report(self, ticker, data):
        self.logger.info(f"""
        {'-' * 40}
        Ticker : {ticker}

        EMA Short          : {data[EMA.SHORT].iloc[-2]}
        EMA Mid            : {data[EMA.MID].iloc[-2]}
        EMA Long           : {data[EMA.LONG].iloc[-2]}
        Stage              : {EMA.get_stage(data)}

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
        {'-' * 40}
        """)