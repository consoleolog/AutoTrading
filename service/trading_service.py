import abc
from pandas import DataFrame
from model.const.stage import Stage
from model.const.timeframe import TimeFrame
from model.entity.candle import Candle
from model.entity.order import Order

class TradingService(abc.ABC):
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