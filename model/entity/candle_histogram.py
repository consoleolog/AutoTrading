from pandas import DataFrame

from model.dto.histogram import Histogram


class CandleHistogram:
    def __init__(
            self,
            candle_id:str=None,
            up:float=None,
            mid:float=None,
            low:float=None,
    ):
        self.candle_id=candle_id
        self.up=up
        self.mid=mid
        self.low=low

    @staticmethod
    def of(candle_id:str, data: DataFrame):
        return CandleHistogram(
            candle_id=candle_id,
            up=float(data[Histogram.UP]),
            mid=float(data[Histogram.MID]),
            low=float(data[Histogram.LOW]),
        )

    def __str__(self):
        return f"""
        CandleHistogram(
            candle_id={self.candle_id},
            up={self.up},
            mid={self.mid},
            low={self.low}    
        )"""