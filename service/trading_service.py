import abc
from pandas import DataFrame
from model.const.stage import Stage
from model.const.timeframe import TimeFrame

class TradingService(abc.ABC):
    @abc.abstractmethod
    def save_data(self, ticker , timeframe: TimeFrame, data, stage: Stage):
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