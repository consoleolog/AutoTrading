from pandas import DataFrame
from logger import LoggerFactory
from multiprocessing.dummy import Pool as ThreadPool
from model.const.timeframe import TimeFrame
from model.dto.ema import EMA
from model.dto.histogram import Histogram
from model.dto.macd import MACD
from utils import data_utils, exchange_utils
from utils.exception.data_exception import DataException

class TradingService:
    def __init__(self, ticker_list):
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        LoggerFactory.set_stream_level(LoggerFactory.INFO)
        self.ticker_list = ticker_list
        self.price_keys = {
            "BTC/KRW": 0.00005,
            "ETH/KRW": 0.0015,
            "BCH/KRW": 0.011,
            "AAVE/KRW": 0.015,
            "SOL/KRW": 0.02,
            "BSV/KRW": 0.1,
            "YFI/KRW": 0.0006,
            "BNB/KRW": 0.007,
            "COMP/KRW": 0.06,
        }

    def start_trading(self, timeframe: TimeFrame):
        pool = ThreadPool(4)
        result = pool.map(lambda ticker: self.auto_trading(ticker, timeframe), self.ticker_list)
        pool.close()
        pool.join()
        self.logger.info(result)

    def auto_trading(self, ticker:str, timeframe: TimeFrame):
        candles = exchange_utils.get_candles(ticker, timeframe)
        data = data_utils.create_sub_data(candles)
        mode, stage = data_utils.select_mode(data)
        krw = exchange_utils.get_krw()
        balance = exchange_utils.get_balance(ticker)
        try:
            if mode == "buy" and data_utils.peekout(data, mode) and data_utils.cross_signal(data) and data_utils.increase(data):
                self._print_trading_report(ticker, data)
                if krw > 8000 and balance == 0:
                    exchange_utils.create_buy_order(ticker, self.price_keys[ticker])

            elif mode == "sell" and data_utils.peekout(data, mode) and data_utils.cross_signal(data) and data_utils.decrease(data):
                self._print_trading_report(ticker, data)
                if balance != 0:
                    exchange_utils.create_sell_order(ticker, balance)
        except DataException:
            pass

    def _print_trading_report(self,ticker:str, data:DataFrame):
        self.logger.info(f"""
        {'-' * 40}
        Ticker : {ticker}
        
        EMA Short          : {data[EMA.SHORT].iloc[-2]}
        EMA Mid            : {data[EMA.MID].iloc[-2]}
        EMA Long           : {data[EMA.LONG].iloc[-2]}
        Stage              : {EMA.get_stage(data)}

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
        {'-' * 40}
        """)