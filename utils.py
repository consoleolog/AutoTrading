import os

import exchange
from dto.ema import EMA
from dto.macd import MACD
from dto.rsi import RSI
from dto.stochastic import Stochastic

def init_file(ticker_list):
    for ticker in ticker_list:
        filename = ticker.split('/')[0]
        with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
            f.write("none")
        with open(f"{os.getcwd()}/{filename}_sell_position.txt", "w") as f:
            f.write("none")

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

    # STOCHASTIC
    stochastic = Stochastic(data, 12, 3, 3)
    data[Stochastic.D_FAST] = stochastic.d_fast
    data[Stochastic.D_SLOW] = stochastic.d_slow
    data[Stochastic.BULLISH] = stochastic.bullish_val
    data[Stochastic.BEARISH] = stochastic.bearish_val


    # RSI
    rsi = RSI(data, 14)
    data[RSI.RSI] = rsi.val
    data[RSI.SIG] = rsi.signal_val
    data[RSI.BULLISH] = rsi.bullish_val
    data[RSI.BEARISH] = rsi.bearish_val

    current_stage = EMA.get_stage(data)

    return current_stage, data

def peekout(data, mode):
    up_hist, mid_hist, low_hist = (
         data[MACD.UP_HIST].iloc[-8:],
        data[MACD.MID_HIST].iloc[-8:],
        data[MACD.LOW_HIST].iloc[-8:],
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
        raise ValueError("Unexpected Mode" + mode)

def macd_bullish(data):
    up, mid = (
        data[MACD.UP_BULLISH].iloc[-3:],
        data[MACD.MID_BULLISH].iloc[-3:],
    )
    return True if (
        up.isin([True]).any() and
        mid.isin([True]).any()
    ) else False

def macd_bearish(data):
    up, mid = (
        data[MACD.UP_BEARISH].iloc[-3:],
        data[MACD.MID_BEARISH].iloc[-3:],
    )
    return True if (
        up.isin([True]).any() and
        mid.isin([True]).any()
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
