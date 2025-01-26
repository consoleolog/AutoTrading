import pandas as pd
from model.dto.ema import EMA

class MACD:
    UP = "MACD_UP"
    MID = "MACD_MID"
    LOW = "MACD_LOW"

    UP_SIGNAL = "MACD_UP_SIGNAL"
    MID_SIGNAL = "MACD_MID_SIGNAL"
    LOW_SIGNAL = "MACD_LOW_SIGNAL"

    UP_GRADIENT = "MACD_UP_GRADIENT"
    MID_GRADIENT = "MACD_MID_GRADIENT"
    LOW_GRADIENT = "MACD_LOW_GRADIENT"

    UP_HISTOGRAM = "MACD_UP_HISTOGRAM"
    MID_HISTOGRAM = "MACD_MID_HISTOGRAM"
    LOW_HISTOGRAM = "MACD_LOW_HISTOGRAM"

    UP_CROSSOVER = "MACD_UP_CROSSOVER"
    MID_CROSSOVER = "MACD_MID_CROSSOVER"
    LOW_CROSSOVER = "MACD_LOW_CROSSOVER"

    UP_BULLISH = "MACD_UP_BULLISH"
    MID_BULLISH = "MACD_MID_BULLISH"
    LOW_BULLISH = "MACD_LOW_BULLISH"

    UP_BEARISH = "MACD_UP_BEARISH"
    MID_BEARISH = "MACD_MID_BEARISH"
    LOW_BEARISH = "MACD_LOW_BEARISH"

    BEARISH = "BEARISH"
    BULLISH = "BULLISH"

    def __init__(self, data:pd.DataFrame ,period_short:int = 12, period_long:int = 26, period_signal: int = 9, column: str = "close"):
        ShortEMA = EMA(data, period_short, column).val
        LongEMA = EMA(data, period_long, column).val

        data[f"MACD_{str(period_short)}_{str(period_long)}"] = ShortEMA - LongEMA
        self.val = data[f"MACD_{str(period_short)}_{str(period_long)}"]
        self.signal_val = EMA(data, period_signal, column = f"MACD_{str(period_short)}_{str(period_long)}").val
        self.histogram_val = self.val - self.signal_val