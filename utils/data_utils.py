import numpy as np
from pandas import DataFrame
from model.const.stage import Stage
from model.dto.ema import EMA
from model.dto.macd import MACD
from utils.exception.data_exception import DataException
from utils.exception.error_response import ErrorResponse

def create_sub_data(data: DataFrame, short_period:int=14, mid_period:int=30, long_period:int=60)->DataFrame:
    # EMA
    data[EMA.SHORT] = EMA(data, short_period).val
    data[EMA.MID] = EMA(data, mid_period).val
    data[EMA.LONG] = EMA(data, long_period).val
    # EMA SLOPE
    data[EMA.SHORT_SLOPE] = (data[EMA.SHORT] - data[EMA.SHORT].shift(3) ) / short_period
    data[EMA.MID_SLOPE] = (data[EMA.MID] - data[EMA.MID].shift(3) ) / mid_period
    data[EMA.LONG_SLOPE] = (data[EMA.LONG] - data[EMA.LONG].shift(1) ) / long_period

    ShortMACD = MACD(data, short_period, mid_period)
    MidMACD = MACD(data, short_period, long_period)
    LowMACD = MACD(data, mid_period, long_period)
    # MACD
    data[MACD.UP] = ShortMACD.val
    data[MACD.MID] = MidMACD.val
    data[MACD.LOW] = LowMACD.val
    # MACD SLOPE
    data[MACD.UP_SLOPE] = (ShortMACD.val - ShortMACD.val.shift(3)) / short_period
    data[MACD.MID_SLOPE] = (MidMACD.val - MidMACD.val.shift(3)) / mid_period
    data[MACD.LOW_SLOPE] = (LowMACD.val - LowMACD.val.shift(3)) / long_period
    # MACD SIGNAL
    data[MACD.UP_SIGNAL] = ShortMACD.signal_val
    data[MACD.MID_SIGNAL] = MidMACD.signal_val
    data[MACD.LOW_SIGNAL] = LowMACD.signal_val
    # MACD GRADIENT
    data[MACD.UP_GRADIENT] = np.gradient(ShortMACD.val)
    data[MACD.MID_GRADIENT] = np.gradient(MidMACD.val)
    data[MACD.LOW_GRADIENT] = np.gradient(LowMACD.val)
    # MACD HISTOGRAM
    data[MACD.UP_HISTOGRAM] = ShortMACD.histogram_val
    data[MACD.MID_HISTOGRAM] = MidMACD.histogram_val
    data[MACD.LOW_HISTOGRAM] = LowMACD.histogram_val
    # MACD CROSSOVER
    data[MACD.UP_CROSSOVER] = np.where(
        (data[MACD.UP].shift(1) < data[MACD.UP_SIGNAL].shift(1)) & (data[MACD.UP] > data[MACD.UP_SIGNAL]), MACD.UP_BULLISH,
        np.where(
            (data[MACD.UP].shift(1) > data[MACD.UP_SIGNAL].shift(1)) & (data[MACD.UP] < data[MACD.UP_SIGNAL]), MACD.UP_BEARISH,
            None
        )
    )
    data[MACD.MID_CROSSOVER] = np.where(
        (data[MACD.MID].shift(1) < data[MACD.MID_SIGNAL].shift(1)) & (data[MACD.MID] > data[MACD.MID_SIGNAL]), MACD.MID_BULLISH,
        np.where(
            (data[MACD.MID].shift(1) > data[MACD.MID_SIGNAL].shift(1)) & (data[MACD.MID] < data[MACD.MID_SIGNAL]), MACD.MID_BEARISH,
            None
        )
    )
    data[MACD.LOW_CROSSOVER] = np.where(
        (data[MACD.LOW].shift(1) < data[MACD.LOW_SIGNAL].shift(1)) & (data[MACD.LOW] > data[MACD.LOW_SIGNAL]), MACD.LOW_BULLISH,
        np.where(
            (data[MACD.LOW].shift(1) > data[MACD.LOW_SIGNAL].shift(1)) & (data[MACD.LOW] < data[MACD.LOW_SIGNAL]), MACD.LOW_BEARISH,
            None
        )
    )
    return data

def select_mode(data:DataFrame) -> tuple[str, Stage]:
    stage = EMA.get_stage(data)
    if stage == Stage.STABLE_INCREASE or stage == Stage.END_OF_INCREASE or stage == Stage.START_OF_DECREASE:
        return "sell", stage
    elif stage == Stage.STABLE_DECREASE or stage == Stage.END_OF_DECREASE or stage == Stage.START_OF_INCREASE:
        return "buy", stage

def peekout(data: DataFrame, mode:str)->bool:
    up_hist, mid_hist, low_hist = (
        data[MACD.UP_HISTOGRAM].iloc[-5:],
        data[MACD.MID_HISTOGRAM].iloc[-5:],
        data[MACD.LOW_HISTOGRAM].iloc[-5:]
    )
    if mode == "buy":
        return all([up_hist.iloc[-1] > up_hist.min(),
                    mid_hist.iloc[-1] > mid_hist.min(),
                    low_hist.iloc[-1] > low_hist.min()])
    elif mode == "sell":
        return all([up_hist.iloc[-1] < up_hist.max(),
                    mid_hist.iloc[-1] < mid_hist.max(),
                    low_hist.iloc[-1] < low_hist.max()
                    ])
    else:
        error = ErrorResponse("BAD_REQUEST", 400, "UnExcepted Data")
        raise DataException(error)

def bullish(data: DataFrame):
    up, mid, low = (
        data[MACD.UP_CROSSOVER].iloc[-5:],
        data[MACD.MID_CROSSOVER].iloc[-5:],
        data[MACD.LOW_CROSSOVER].iloc[-5:]
    )
    return True if (
            up.isin([MACD.UP_BULLISH]).any() and
            mid.isin([MACD.MID_BULLISH]).any()
    ) else False

def bearish(data: DataFrame):
    up, mid, low = (
        data[MACD.UP_CROSSOVER].iloc[-5:],
        data[MACD.MID_CROSSOVER].iloc[-5:],
        data[MACD.LOW_CROSSOVER].iloc[-5:]
    )
    return (
        up.isin([MACD.UP_BEARISH]).any() and
        mid.isin([MACD.MID_BEARISH]).any() and
        low.isin([MACD.LOW_BEARISH]).any()
    )

def Up(data: DataFrame):
    up, mid, low = (
        data[MACD.UP_GRADIENT].iloc[-5:],
        data[MACD.MID_GRADIENT].iloc[-5:],
        data[MACD.LOW_GRADIENT].iloc[-5:],
    )
    return True if (
        up.mean() > 0,
        mid.mean() > 0,
        low.mean() > 0
    ) else False
def Down(data: DataFrame):
    up, mid, low = (
       data[MACD.UP_GRADIENT].iloc[-5:],
       data[MACD.MID_GRADIENT].iloc[-5:],
       data[MACD.LOW_GRADIENT].iloc[-5:],
    )
    return True if (
        up.mean() < 0,
        mid.mean() < 0,
        low.mean() < 0
    ) else False

def increase(data: DataFrame):
    (ema_short, ema_mid, ema_long,
     macd_up, macd_mid, macd_low) = (
        data[EMA.SHORT_SLOPE].iloc[-5:],
        data[EMA.MID_SLOPE].iloc[-5:],
        data[EMA.LONG_SLOPE].iloc[-5:],
        data[MACD.UP_GRADIENT].iloc[-5:],
        data[MACD.MID_GRADIENT].iloc[-5:],
        data[MACD.LOW_GRADIENT].iloc[-5:],
    )
    return all([
        ema_short.mean() > 0,
        ema_mid.mean() > 0,
        ema_long.mean() > 0,
        macd_up.mean() > 0,
        macd_mid.mean() > 0,
        macd_low.mean() > 0,
    ])

def decrease(data: DataFrame):
    short, mid, long = (
        data[EMA.SHORT_SLOPE].iloc[-5:],
        data[EMA.MID_SLOPE].iloc[-5:],
        data[EMA.LONG_SLOPE].iloc[-5:],
    )
    return True if (
        short.mean() < 0,
        mid.mean() < 0,
        long.mean() < 0
    ) else False
