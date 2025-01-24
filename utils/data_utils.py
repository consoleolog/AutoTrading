import numpy as np
from pandas import DataFrame

from model.const.stage import Stage
from model.dto.ema import EMA
from model.dto.macd import MACD
from utils.exception.data_exception import DataException
from utils.exception.error_response import ErrorResponse

def create_sub_data(data: DataFrame, short_period:int=14, mid_period:int=30, long_period:int=60):
    data[EMA.SHORT] = EMA(data, short_period).val
    data[EMA.MID] = EMA(data, mid_period).val
    data[EMA.LONG] = EMA(data, long_period).val

    ShortMACD = MACD(data, short_period, mid_period)
    MidMACD = MACD(data, short_period, long_period)
    LowMACD = MACD(data, mid_period, long_period)

    data[MACD.UP] = ShortMACD.val
    data[MACD.MID] = MidMACD.val
    data[MACD.LOW] = LowMACD.val

    data[MACD.UP_SIGNAL] = ShortMACD.signal_val
    data[MACD.MID_SIGNAL] = MidMACD.signal_val
    data[MACD.LOW_SIGNAL] = LowMACD.signal_val

    data[MACD.UP_GRADIENT] = np.gradient(ShortMACD.val)
    data[MACD.MID_GRADIENT] = np.gradient(MidMACD.val)
    data[MACD.LOW_GRADIENT] = np.gradient(LowMACD.val)

    data[MACD.UP_HISTOGRAM] = ShortMACD.histogram_val
    data[MACD.MID_HISTOGRAM] = MidMACD.histogram_val
    data[MACD.LOW_HISTOGRAM] = LowMACD.histogram_val

    return data

def select_mode(data:DataFrame) -> tuple[str, Stage]:
    stage = EMA.get_stage(data)
    if stage == Stage.STABLE_INCREASE or stage == Stage.END_OF_INCREASE or stage == Stage.START_OF_DECREASE:
        return "sell", stage
    elif stage == Stage.STABLE_DECREASE or stage == Stage.END_OF_DECREASE or stage == Stage.START_OF_INCREASE:
        return "buy", stage


def peekout(data: DataFrame, mode:str)->bool:
    up_hist, mid_hist, low_hist = data[MACD.UP_HISTOGRAM], data[MACD.MID_HISTOGRAM], data[MACD.LOW_HISTOGRAM]
    if mode == "buy":
        return all([up_hist.iloc[-1] > up_hist.min(),
                    mid_hist.iloc[-1] > mid_hist.min(),
                    low_hist.iloc[-1] > low_hist.min()])
    elif mode == "sell":
        return all([up_hist.iloc[-1] < up_hist.max(),
                    mid_hist.iloc[-1] < mid_hist.max(),
                    low_hist.iloc[-1] < low_hist.max()])
    else:
        error = ErrorResponse("BAD_REQUEST", 400, "UnExcepted Data")
        raise DataException(error)

def cross_signal(data: DataFrame) -> bool:
    up, mid, low = data[MACD.UP], data[MACD.MID], data[MACD.LOW]
    up_signal, mid_signal, low_signal = data[MACD.UP_SIGNAL], data[MACD.MID_SIGNAL], data[MACD.LOW_SIGNAL]

    before = up.iloc[-1] > up_signal.iloc[-1]
    after = up.iloc[-2] > up_signal.iloc[-2]
    if before != after:
        return True
    else:
        return False

def increase(data: DataFrame) -> bool:
    up_gradient, mid_gradient, low_gradient = data[MACD.UP_GRADIENT], data[MACD.MID_GRADIENT], data[MACD.LOW_GRADIENT]
    return all([up_gradient.iloc[-1] > up_gradient.iloc[-2] > 0,
                mid_gradient.iloc[-1] > mid_gradient.iloc[-2] > 0,
                low_gradient.iloc[-1] > low_gradient.iloc[-2] > 0])

def decrease(data: DataFrame) -> bool:
    up_gradient, mid_gradient, low_gradient = data[MACD.UP_GRADIENT], data[MACD.MID_GRADIENT], data[MACD.LOW_GRADIENT]
    return all([up_gradient.iloc[-1]  < up_gradient.iloc[-2],
                mid_gradient.iloc[-1] <  mid_gradient.iloc[-2],
                low_gradient.iloc[-1] <  low_gradient.iloc[-2]])