import numpy as np


def EMA(data, period: int):
    return data.ewm(span=period, adjust=False).mean()


def MACD(data, short_period, long_period, signal_period=9, returns=("value",)):
    ShortEMA = EMA(data["close"], short_period)
    LongEMA = EMA(data["close"], long_period)
    # MACD
    value = ShortEMA - LongEMA
    # MACD SIGNAL
    signal = EMA(value, signal_period)
    # MACD HISTOGRAM
    oscillator = value - signal
    golden_cross = (value.shift(1) < signal.shift(1)) & (value > signal)
    dead_cross = (value.shift(1) > signal.shift(1)) & (value < signal)
    variables = locals()
    return tuple(variables[r] for r in returns)


def RSI(data, period=14, signal_period=9, returns=("value",)):
    delta = data["close"].diff()
    U = delta.clip(lower=0)
    D = -delta.clip(upper=0)
    AU = U.ewm(com=period - 1, min_periods=1).mean()
    AD = D.ewm(com=period - 1, min_periods=1).mean()

    rs = AU / AD
    rs.replace([np.inf, -np.inf], np.nan, inplace=True)
    rs.fillna(0, inplace=True)

    value = 100 - (100 / (1 + rs))
    signal = EMA(value, signal_period)
    oscillator = value - signal
    golden_cross = (value.shift(1) < signal.shift(1)) & (value > signal)
    dead_cross = (value.shift(1) > signal.shift(1)) & (value < signal)
    variables = locals()
    return tuple(variables[r] for r in returns)


def Stochastic(data, k_len=10, k_smooth=6, d_smooth=6, returns=("k_slow", "d_slow")):
    low_price = data["low"].rolling(window=k_len, min_periods=1).min()
    high_price = data["high"].rolling(window=k_len, min_periods=1).max()
    k_fast = ((data["close"] - low_price) / (high_price - low_price)) * 100.0

    k_slow = k_fast.rolling(window=k_smooth, min_periods=1).mean()
    d_fast = k_fast.rolling(window=k_smooth, min_periods=1).mean()
    d_slow = d_fast.rolling(window=d_smooth, min_periods=1).mean()
    golden_cross = (d_fast.shift(1) < d_slow.shift(1)) & (d_fast > d_slow)
    dead_cross = (d_fast.shift(1) > d_slow.shift(1)) & (d_fast < d_slow)
    variables = locals()
    return tuple(variables[r] for r in returns)
