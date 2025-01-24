import abc
from model.const.timeframe import TimeFrame
from model.entity.candle import Candle
from model.entity.candle_ema import CandleEMA
from model.entity.candle_macd import CandleMACD

class CandleRepository(abc.ABC):

    @abc.abstractmethod
    def find_all(self):
        pass
    @abc.abstractmethod
    def find_all_by_ticker(self, ticker: str):
        pass
    @abc.abstractmethod
    def find_all_by_ticker_and_timeframe(self, ticker:str, timeframe: TimeFrame):
        pass
    @abc.abstractmethod
    def save_candle(self, candle: Candle)->Candle:
        pass
    @abc.abstractmethod
    def save_candle_ema(self, candle_ema: CandleEMA)->CandleEMA:
        pass
    @abc.abstractmethod
    def save_candle_macd(self, candle_macd: CandleMACD)->CandleMACD:
        pass