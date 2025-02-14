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
    ShortMACD = MACD(data,10, 20)
    data[MACD.SHORT] = ShortMACD.val
    data[MACD.SHORT_SIG] = ShortMACD.signal_val
    data[MACD.SHORT_HIST] = ShortMACD.histogram_val
    data[MACD.SHORT_BULLISH] = ShortMACD.bullish_val
    data[MACD.SHORT_BEARISH] = ShortMACD.bearish_val

    LongMACD = MACD(data, 12, 26)
    data[MACD.LONG] = LongMACD.val
    data[MACD.LONG_SIG] = LongMACD.signal_val
    data[MACD.LONG_HIST] = LongMACD.histogram_val
    data[MACD.LONG_BULLISH] = LongMACD.bullish_val
    data[MACD.LONG_BEARISH] = LongMACD.bearish_val

    # STOCHASTIC
    stochastic = Stochastic(data, 12, 3, 3)
    data[Stochastic.K_SLOW] = stochastic.d_fast
    data[Stochastic.D_FAST] = stochastic.d_fast
    data[Stochastic.D_SLOW] = stochastic.d_slow
    data[Stochastic.BULLISH] = stochastic.bullish_val
    data[Stochastic.BEARISH] = stochastic.bearish_val

    # RSI
    ShortRSI = RSI(data, 9)
    data[RSI.SHORT] = ShortRSI.val
    data[RSI.SHORT_SIG] = ShortRSI.signal_val
    data[RSI.SHORT_BULLISH] = ShortRSI.bullish_val
    data[RSI.SHORT_BEARISH] = ShortRSI.bearish_val

    LongRSI = RSI(data, 14)
    data[RSI.LONG] = LongRSI.val
    data[RSI.LONG_SIG] = LongRSI.signal_val
    data[RSI.LONG_BULLISH] = LongRSI.bullish_val
    data[RSI.LONG_BEARISH] = LongRSI.bearish_val

    current_stage = EMA.get_stage(data)

    return current_stage, data