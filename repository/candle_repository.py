import psycopg2

from logger import LoggerFactory
from model.entity.candle import Candle
from model.entity.candle_ema import CandleEMA
from model.entity.candle_macd import CandleMACD


class CandleRepository:
    def __init__(self, connection):
        self.connection = connection
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")

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
                    STAGE 
                ) VALUES ( %s, %s, %s, %s, %s )
                """,(candle_ema.candle_id,
                     candle_ema.short,
                     candle_ema.mid,
                     candle_ema.long,
                     candle_ema.stage))
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