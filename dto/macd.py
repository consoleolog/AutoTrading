import pandas as pd
from dto.ema import EMA

class MACD:
    SHORT = "MACD_SHORT"
    SHORT_SIG = "MACD_SHORT_SIGNAL"
    SHORT_HIST = "MACD_SHORT_HIST"
    SHORT_BULLISH = "MACD_SHORT_BULLISH"
    SHORT_BEARISH = "MACD_SHORT_BEARISH"

    MID = "MACD_MID"
    MID_SIG = "MACD_MID_SIGNAL"
    MID_HIST = "MACD_MID_HIST"
    MID_BULLISH = "MACD_MID_BULLISH"
    MID_BEARISH = "MACD_MID_BEARISH"

    LONG = "MACD_LONG"
    LONG_SIG = "MACD_LONG_SIGNAL"
    LONG_HIST = "MACD_LONG_HIST"
    LONG_BULLISH = "MACD_LONG_BULLISH"
    LONG_BEARISH = "MACD_LONG_BEARISH"

    def __init__(self, data:pd.DataFrame ,period_short:int = 12, period_long:int = 26, period_signal: int = 9):
        ShortEMA = EMA(data["close"], period_short).val
        LongEMA = EMA(data["close"], period_long).val

        self.val = ShortEMA - LongEMA
        self.signal_val = EMA(self.val, period_signal).val
        self.histogram_val = self.val - self.signal_val
        self.bullish_val = (self.val.shift(1) < self.signal_val.shift(1)) & (self.val > self.signal_val)
        self.bearish_val = (self.val.shift(1) > self.signal_val.shift(1)) & (self.val < self.signal_val)
