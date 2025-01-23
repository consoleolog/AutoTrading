import numpy as np
from pandas import DataFrame

from model.const.stage import Stage
from model.dto.ema import EMA
from model.dto.histogram import Histogram
from model.dto.macd import MACD

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

    data[Histogram.UP] = ShortMACD.val - ShortMACD.signal_val
    data[Histogram.MID] = MidMACD.val - MidMACD.signal_val
    data[Histogram.LOW] = LowMACD.val - LowMACD.signal_val

    return data

def select_mode(data:DataFrame) -> tuple[str, Stage]:
    stage = EMA.get_stage(data)
    if stage == Stage.STABLE_INCREASE or stage == Stage.END_OF_INCREASE or stage == Stage.START_OF_DECREASE:
        return "buy", stage
    elif stage == Stage.STABLE_DECREASE or stage == Stage.END_OF_DECREASE or stage == Stage.START_OF_INCREASE:
        return "sell", stage


