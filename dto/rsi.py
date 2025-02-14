import numpy as np
from pandas import DataFrame

from dto.ema import EMA


class RSI:
    SHORT = "RSI_SHORT"
    SHORT_SIG = "RSI_SHORT_SIGNAL"
    SHORT_BULLISH = "RSI_SHORT_BULLISH"
    SHORT_BEARISH = "RSI_SHORT_BEARISH"

    LONG = "RSI_LONG"
    LONG_SIG = "RSI_LONG_SIGNAL"
    LONG_BULLISH = "RSI_LONG_BULLISH"
    LONG_BEARISH = "RSI_LONG_BEARISH"

    def __init__(self, data: DataFrame, period=14, period_sigal = 9):
        delta = data["close"].diff()
        U = delta.clip(lower=0)  # 상승한 날은 그대로, 나머지는 0
        D = -delta.clip(upper=0)  # 하락한 날은 양수로 변환, 나머지는 0
        AU = U.ewm(com=period - 1, min_periods=period).mean()
        AD = D.ewm(com=period - 1, min_periods=period).mean()

        rs = AU / AD
        rs.replace([np.inf, -np.inf], np.nan, inplace=True)
        rs.fillna(0, inplace=True)

        rsi = 100 - (100 / (1 + rs))
        self.val = rsi
        self.signal_val = EMA(self.val, period_sigal).val
        self.histogram_val = self.val - self.signal_val
        self.bullish_val = ((self.val.shift(1) < self.signal_val.shift(1)) & (self.val > self.signal_val))
        self.bearish_val = ((self.val.shift(1) > self.signal_val.shift(1)) & (self.val < self.signal_val))
