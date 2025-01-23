from model.dto.macd import MACD


class CandleMACD:
    def __init__(
        self,
        candle_id:str = None,
        up: float = None,
        mid: float = None,
        low : float = None,
        up_signal: float = None,
        mid_signal: float = None,
        low_signal: float = None,
        up_slope: float = None,
        mid_slope: float = None,
        low_slope: float = None,
    ):
        self.candle_id = candle_id
        self.up = up
        self.mid = mid
        self.low = low
        self.up_signal = up_signal
        self.mid_signal = mid_signal
        self.low_signal = low_signal
        self.up_slope = up_slope
        self.mid_slope = mid_slope
        self.low_slope = low_slope

    @staticmethod
    def of(candle_id, df):
        return CandleMACD(
            candle_id=candle_id,
            up=float(df[MACD.UP].iloc[-1]),
            mid=float(df[MACD.MID].iloc[-1]),
            low=float(df[MACD.LOW].iloc[-1]),
            up_signal=float(df[MACD.UP_SIGNAL].iloc[-1]),
            mid_signal=float(df[MACD.MID_SIGNAL].iloc[-1]),
            low_signal=float(df[MACD.LOW_SIGNAL].iloc[-1]),
            up_slope=float(df[MACD.UP_SLOPE].iloc[-1]),
            mid_slope=float(df[MACD.MID_SLOPE].iloc[-1]),
            low_slope=float(df[MACD.LOW_SLOPE].iloc[-1]),
        )

    def __str__(self):
        return f"""
        CandleMACD(
            candle_id={self.candle_id},
            up={self.up},
            mid={self.mid},
            low={self.low},
            up_signal={self.up_signal},
            mid_signal={self.mid_signal},
            low_signal={self.low_signal},
            up_slope={self.up_slope},
            mid_slope={self.mid_slope},
            low_slope={self.low_slope},
        )"""