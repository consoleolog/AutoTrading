import pandas as pd
from model.dto.ema import EMA

class MACD:
    UP = "MACD_UP"
    MID = "MACD_MID"
    LOW = "MACD_LOW"

    UP_SIGNAL = "MACD_UP_SIGNAL"
    MID_SIGNAL = "MACD_MID_SIGNAL"
    LOW_SIGNAL = "MACD_LOW_SIGNAL"

    UP_SLOPE = "MACD_UP_SLOPE"
    MID_SLOPE = "MACD_MID_SLOPE"
    LOW_SLOPE = "MACD_LOW_SLOPE"

    def __init__(self, data:pd.DataFrame ,period_short:int = 12, period_long:int = 26, period_signal: int = 9, column: str = "close"):
        ShortEMA = EMA(data, period_short, column).val
        LongEMA = EMA(data, period_long, column).val

        data[f"MACD_{str(period_short)}_{str(period_long)}"] = ShortEMA - LongEMA
        self.value = data[f"MACD_{str(period_short)}_{str(period_long)}"]
        self.signal_value = EMA(data, period_signal, column = f"MACD_{str(period_short)}_{str(period_long)}").val