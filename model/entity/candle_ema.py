from pandas import DataFrame
from model.const.stage import Stage
from model.dto.ema import EMA

class CandleEMA:
    def __init__(
            self,
            candle_id: str = None,
            short: float = None,
            mid: float = None,
            long: float = None,
            stage: Stage = None,
            short_slope: float = None,
            mid_slope: float = None,
            long_slope: float = None,
    ):
        self.candle_id = candle_id
        self.short = short
        self.mid = mid
        self.long = long
        self.stage = stage
        self.short_slope = short_slope
        self.mid_slope = mid_slope
        self.long_slope = long_slope

    @staticmethod
    def of(candle_id: str, stage: Stage,df: DataFrame):
        return CandleEMA(
            candle_id=candle_id,
            short=float(df[EMA.SHORT].iloc[-1]),
            mid=float(df[EMA.MID].iloc[-1]),
            long=float(df[EMA.LONG].iloc[-1]),
            short_slope=float(df[EMA.SHORT_SLOPE].iloc[-1]),
            mid_slope=float(df[EMA.MID_SLOPE].iloc[-1]),
            long_slope=float(df[EMA.LONG_SLOPE].iloc[-1]),
            stage=stage
        )

    def __str__(self):
        return f"""
        CandleEMA(
            candle_id={self.candle_id},
            short={self.short},
            mid={self.mid},
            long={self.long},
            short_slope={self.short_slope},
            mid_slope={self.mid_slope},
            long_slope={self.long_slope},
            stage={self.stage}
        )"""