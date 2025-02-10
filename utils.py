import exchange
from dto.ema import EMA
from dto.macd import MACD
from dto.rsi import RSI

def get_data(ticker, timeframe, short_period = 5, mid_period= 20, long_period = 40):
    data = exchange.get_candles(ticker, timeframe)

    # EMA
    data[EMA.SHORT] = EMA(data["close"], short_period).val
    data[EMA.MID] = EMA(data["close"], mid_period).val
    data[EMA.LONG] = EMA(data["close"], long_period).val

    # MACD
    ShortMACD = MACD(data, short_period, mid_period)
    MidMACD = MACD(data, short_period, long_period)
    LowMACD = MACD(data, mid_period, long_period)

    data[MACD.UP] = ShortMACD.val
    data[MACD.MID] = MidMACD.val
    data[MACD.LOW] = LowMACD.val
    # SIGNAL
    data[MACD.UP_SIG] = ShortMACD.signal_val
    data[MACD.MID_SIG] = MidMACD.signal_val
    data[MACD.LOW_SIG] = LowMACD.signal_val

    # HISTOGRAM
    data[MACD.UP_HIST] = ShortMACD.histogram_val
    data[MACD.MID_HIST] = MidMACD.histogram_val
    data[MACD.LOW_HIST] = LowMACD.histogram_val

    # BULLISH
    data[MACD.UP_BULLISH] = ShortMACD.bullish_val
    data[MACD.MID_BULLISH] = MidMACD.bullish_val
    data[MACD.LOW_BULLISH] = LowMACD.bullish_val

    # BEARISH
    data[MACD.UP_BEARISH] = ShortMACD.bearish_val
    data[MACD.MID_BEARISH] = MidMACD.bearish_val
    data[MACD.LOW_BEARISH] = LowMACD.bearish_val

    # RSI
    rsi = RSI(data, 9)
    data[RSI.RSI] = rsi.val
    data[RSI.SIG] = rsi.signal_val
    data[RSI.BULLISH] = rsi.bullish_val
    data[RSI.BEARISH] = rsi.bearish_val

    current_stage = EMA.get_stage(data)

    return current_stage, data

def peekout(data, mode):
    up_hist, mid_hist, low_hist = (
         data[MACD.UP_HIST].iloc[-5:],
        data[MACD.MID_HIST].iloc[-5:],
        data[MACD.LOW_HIST].iloc[-5:],
    )
    if mode == "buy":
        return all([up_hist.iloc[-1] > up_hist.min(),
                    mid_hist.iloc[-1] > mid_hist.min(),
                    low_hist.iloc[-1] > low_hist.min()])
    elif mode == "sell":
        return all([up_hist.iloc[-1] < up_hist.max(),
                    mid_hist.iloc[-1] < mid_hist.max(),
                    low_hist.iloc[-1] < low_hist.max()])
    else:
        raise ValueError("UnExcepted Mode" + mode)

def bullish(data):
    up, mid, low, rsi = (
        data[MACD.UP_BULLISH].iloc[-5:],
        data[MACD.MID_BULLISH].iloc[-5:],
        data[MACD.LOW_BULLISH].iloc[-5:],
        data[RSI.BULLISH].iloc[-5:],
    )
    return True if (
        up.isin([True]).any() and
        mid.isin([True]).any() and
        low.isin([True]).any() and
        rsi.isin([True]).any()
    ) else False

def bearish(data):
    up, mid, low, rsi = (
        data[MACD.UP_BEARISH].iloc[-5:],
        data[MACD.MID_BEARISH].iloc[-5:],
        data[MACD.LOW_BEARISH].iloc[-5:],
        data[RSI.BEARISH].iloc[-5:],
    )
    return True if (
        up.isin([True]).any() and
        mid.isin([True]).any() and
        low.isin([True]).any() and
        rsi.isin([True]).any()
    ) else False
