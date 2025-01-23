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
            stage: Stage = None
    ):
        self.candle_id = candle_id
        self.short = short
        self.mid = mid
        self.long = long
        self.stage = stage

    @staticmethod
    def of(candle_id: str, stage: Stage,df: DataFrame):
        return CandleEMA(
            candle_id=candle_id,
            short=float(df[EMA.SHORT]),
            mid=float(df[EMA.MID]),
            long=float(df[EMA.LONG]),
            stage=stage
        )

    def __str__(self):
        return f"""
        CandleEMA(
            candle_id={self.candle_id},
            short={self.short},
            mid={self.mid},
            long={self.long},
            stage={self.stage}
        )"""