import pickle
import exchange
from dto.ema import EMA
from dto.macd import MACD
from dto.rsi import RSI
from dto.stochastic import Stochastic

def init(ticker_list):
    try:
        with open("info.plk", "rb") as f:
            info = pickle.load(f)
    except FileNotFoundError:
        info = {}
    for ticker in ticker_list:
        if ticker not in info:
            info[ticker] = {
                "position": "long",
                "stoch": False,
                "macd": False,
                "rsi": False,
            }
    with open("info.plk", "wb") as f:
        pickle.dump(info, f)


def get_data(ticker, timeframe, short_period = 5, mid_period= 20, long_period = 40):
    data = exchange.get_candles(ticker, timeframe)

    # EMA
    data[EMA.SHORT] = EMA(data["close"], short_period).val
    data[EMA.MID] = EMA(data["close"], mid_period).val
    data[EMA.LONG] = EMA(data["close"], long_period).val

    # MACD
    macd = MACD(data, 10, 20,9)
    data[MACD.MACD] = macd.val
    data[MACD.SIG] = macd.signal_val
    data[MACD.HIST] = macd.histogram_val
    data[MACD.BULLISH] = macd.bullish_val
    data[MACD.BEARISH] = macd.bearish_val

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
