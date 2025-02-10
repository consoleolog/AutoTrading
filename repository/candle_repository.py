import abc
import pandas as pd
import psycopg2
from logger import LoggerFactory
from constant.timeframe import TimeFrame
from entity.candle import Candle
from entity.candle_ema import CandleEMA
from entity.candle_macd import CandleMACD

class ICandleRepository(abc.ABC):
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

class CandleRepository(ICandleRepository):
    def __init__(self, connection, engine):
        self.connection = connection
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        self.engine = engine

    def find_all(self):
        sql = """SELECT C.CANDLE_ID,
                         C.CREATED_AT,
                         C.TICKER,
                         C.TIMEFRAME,
                         C.CLOSE,
                         C.EMA_SHORT,
                         C.EMA_MID,
                         C.EMA_LONG,
                         C.STAGE,
                         C.MACD_UP,
                         C.MACD_MID,
                         C.MACD_LOW,
                         C.MACD_UP_SIGNAL,
                         C.MACD_MID_SIGNAL,
                         C.MACD_LOW_SIGNAL,
                         C.MACD_UP_GRADIENT,
                         C.MACD_MID_GRADIENT,
                         C.MACD_LOW_GRADIENT
               FROM public.get_candles() AS C;"""
        return pd.read_sql(sql, self.engine)

    def find_all_by_ticker(self, ticker: str):
        sql = """
        SELECT C.CANDLE_ID,
               C.CREATED_AT,
               C.TICKER,
               C.TIMEFRAME,
               C.CLOSE,
               C.EMA_SHORT,
               C.EMA_MID,
               C.EMA_LONG,
               C.STAGE,
               C.MACD_UP,
               C.MACD_MID,
               C.MACD_LOW,
               C.MACD_UP_SIGNAL,
               C.MACD_MID_SIGNAL,
               C.MACD_LOW_SIGNAL,
               C.MACD_UP_GRADIENT,
               C.MACD_MID_GRADIENT,
               C.MACD_LOW_GRADIENT
        FROM public.get_candles_by_ticker(%(ticker)s) AS C
        ORDER BY C.CREATED_AT;
        """
        params = {"ticker": ticker}
        return pd.read_sql(sql, self.engine, params=params)

    def find_all_by_ticker_and_timeframe(self, ticker:str, timeframe: TimeFrame):
        sql = """SELECT C.CANDLE_ID,
                         C.CREATED_AT,
                         C.TICKER,
                         C.TIMEFRAME,
                         C.CLOSE,
                         C.EMA_SHORT,
                         C.EMA_MID,
                         C.EMA_LONG,
                         C.STAGE,
                         C.MACD_UP,
                         C.MACD_MID,
                         C.MACD_LOW,
                         C.MACD_UP_SIGNAL,
                         C.MACD_MID_SIGNAL,
                         C.MACD_LOW_SIGNAL,
                         C.MACD_UP_GRADIENT,
                         C.MACD_MID_GRADIENT,
                         C.MACD_LOW_GRADIENT
               FROM public.get_candles_by_ticker_and_timeframe(%(ticker)s, %(timeframe)s) AS C
               ORDER BY C.CREATED_AT;"""
        params = {"ticker": ticker, "timeframe": timeframe}
        return pd.read_sql(sql, self.engine, params=params)

    def save_candle(self, candle: Candle)->Candle:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO CANDLE (
                    CANDLE_ID,
                    CREATE_AT,
                    TICKER,
                    CLOSE,
                    TIMEFRAME 
                ) VALUES ( %s, %s, %s, %s, %s )
                """,(candle.candle_id,
                    candle.create_at,
                    candle.ticker,
                    candle.close,
                    candle.timeframe
                    ))
            self.connection.commit()
            return candle
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()

    def save_candle_ema(self, candle_ema: CandleEMA)->CandleEMA:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO CANDLE_EMA(
                    CANDLE_ID, 
                    EMA_SHORT, 
                    EMA_MID,
                    EMA_LONG , 
                    STAGE ,
                    EMA_SHORT_SLOPE,
                    EMA_MID_SLOPE,
                    EMA_LONG_SLOPE
                ) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s )
                """,(candle_ema.candle_id,
                     candle_ema.short,
                     candle_ema.mid,
                     candle_ema.long,
                     candle_ema.stage,
                     candle_ema.short_slope,
                     candle_ema.mid_slope,
                     candle_ema.long_slope))
            self.connection.commit()
            return candle_ema
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()

    def save_candle_macd(self, candle_macd: CandleMACD)->CandleMACD:
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO CANDLE_MACD(
                    CANDLE_ID, 
                    MACD_UP, 
                    MACD_MID, 
                    MACD_LOW, 
                    MACD_UP_SIGNAL,
                    MACD_MID_SIGNAL, 
                    MACD_LOW_SIGNAL, 
                    MACD_UP_GRADIENT, 
                    MACD_MID_GRADIENT, 
                    MACD_LOW_GRADIENT, 
                    MACD_UP_HISTOGRAM, 
                    MACD_MID_HISTOGRAM, 
                    MACD_LOW_HISTOGRAM
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """, (candle_macd.candle_id,
                      candle_macd.up,
                      candle_macd.mid,
                      candle_macd.low,
                      candle_macd.up_signal,
                      candle_macd.mid_signal,
                      candle_macd.low_signal,
                      candle_macd.up_gradient,
                      candle_macd.mid_gradient,
                      candle_macd.low_gradient,
                      candle_macd.up_histogram,
                      candle_macd.mid_histogram,
                      candle_macd.low_histogram,))
            self.connection.commit()
            return candle_macd
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()