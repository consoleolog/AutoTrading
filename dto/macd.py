import pandas as pd
from dto.ema import EMA

class MACD:
    MACD = "MACD"

    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    SIG = "SIGNAL"
    HIST = "HISTOGRAM"

    UP = "MACD_UP"
    MID = "MACD_MID"
    LOW = "MACD_LOW"

    UP_SIG = "MACD_UP_SIGNAL"
    MID_SIG = "MACD_MID_SIGNAL"
    LOW_SIG = "MACD_LOW_SIGNAL"

    UP_BULLISH = "MACD_UP_BULLISH"
    MID_BULLISH = "MACD_MID_BULLISH"
    LOW_BULLISH = "MACD_LOW_BULLISH"

    UP_BEARISH = "MACD_UP_BEARISH"
    MID_BEARISH = "MACD_MID_BEARISH"
    LOW_BEARISH = "MACD_LOW_BEARISH"

    UP_HIST = "MACD_UP_HISTOGRAM"
    MID_HIST = "MACD_MID_HISTOGRAM"
    LOW_HIST = "MACD_LOW_HISTOGRAM"

    def __init__(self, data:pd.DataFrame ,period_short:int = 12, period_long:int = 26, period_signal: int = 9):
        ShortEMA = EMA(data["close"], period_short).val
        LongEMA = EMA(data["close"], period_long).val

        self.val = ShortEMA - LongEMA
        self.signal_val = EMA(self.val, period_signal).val
        self.histogram_val = self.val - self.signal_val
        self.bullish_val = (self.val.shift(1) < self.signal_val.shift(1)) & (self.val > self.signal_val)
        self.bearish_val = (self.val.shift(1) > self.signal_val.shift(1)) & (self.val < self.signal_val)
