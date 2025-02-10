from dto.macd import MACD


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
        up_gradient: float = None,
        mid_gradient: float = None,
        low_gradient: float = None,
        up_histogram: float = None,
        mid_histogram: float = None,
        low_histogram: float = None,
    ):
        self.candle_id = candle_id
        self.up = up
        self.mid = mid
        self.low = low
        self.up_signal = up_signal
        self.mid_signal = mid_signal
        self.low_signal = low_signal
        self.up_gradient = up_gradient
        self.mid_gradient = mid_gradient
        self.low_gradient = low_gradient
        self.up_histogram = up_histogram
        self.mid_histogram = mid_histogram
        self.low_histogram = low_histogram

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
            up_gradient=float(df[MACD.UP_GRADIENT].iloc[-1]),
            mid_gradient=float(df[MACD.MID_GRADIENT].iloc[-1]),
            low_gradient=float(df[MACD.LOW_GRADIENT].iloc[-1]),
            up_histogram=float(df[MACD.UP_HISTOGRAM].iloc[-1]),
            mid_histogram=float(df[MACD.MID_HISTOGRAM].iloc[-1]),
            low_histogram=float(df[MACD.LOW_HISTOGRAM].iloc[-1]),
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
            up_gradient={self.up_gradient},
            mid_gradient={self.mid_gradient},
            low_gradient={self.low_gradient},
            up_histogram={self.up_histogram},
            mid_histogram={self.mid_histogram},
            low_histogram={self.low_histogram}
        )"""