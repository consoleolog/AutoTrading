import numpy as np
from pandas import DataFrame
from model.const.stage import Stage
from model.dto.ema import EMA
from model.dto.macd import MACD
from utils.exception.data_exception import DataException
from utils.exception.error_response import ErrorResponse

def create_sub_data(data: DataFrame, short_period:int=14, mid_period:int=30, long_period:int=60)->DataFrame:
    data[EMA.SHORT] = EMA(data, short_period).val
    data[EMA.MID] = EMA(data, mid_period).val
    data[EMA.LONG] = EMA(data, long_period).val

    data[EMA.SHORT_SLOPE] = (data[EMA.SHORT] - data[EMA.SHORT].shift(3) ) / short_period
    data[EMA.MID_SLOPE] = (data[EMA.MID] - data[EMA.MID].shift(3) ) / mid_period
    data[EMA.LONG_SLOPE] = (data[EMA.LONG] - data[EMA.LONG].shift(1) ) / long_period

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


def cross_signal(data: DataFrame):
    up_crossover, mid_crossover, low_crossover = (
        data[MACD.UP_CROSSOVER].iloc[-5:],
        data[MACD.MID_CROSSOVER].iloc[-5:],
        data[MACD.LOW_CROSSOVER].iloc[-5:],
    )

    if (
        up_crossover.isin([MACD.UP_BULLISH]).any() and
        mid_crossover.isin([MACD.MID_BULLISH]).any() and
        low_crossover.isin([MACD.LOW_BULLISH]).any()
    ):
        return MACD.BULLISH

    if (
        up_crossover.isin([MACD.UP_BEARISH]).any() and
        mid_crossover.isin([MACD.MID_BEARISH]).any()
    ):
        return MACD.BEARISH

def increase(data: DataFrame) -> bool:
    up_gradient, mid_gradient, low_gradient = data[MACD.UP_GRADIENT], data[MACD.MID_GRADIENT], data[MACD.LOW_GRADIENT]
    ema_up_slope, ema_mid_slope, ema_long_slope = data[EMA.SHORT_SLOPE], data[EMA.MID_SLOPE], data[EMA.LONG_SLOPE]
    return all([up_gradient.iloc[-1]  > 0,
                up_gradient.iloc[-2]  > 0,
                mid_gradient.iloc[-1] > 0,
                mid_gradient.iloc[-2] > 0,
                low_gradient.iloc[-1] > 0,
                low_gradient.iloc[-2] > 0,
                ema_up_slope.iloc[-1] > 0,
                ema_up_slope.iloc[-2] > 0,
                ema_mid_slope.iloc[-1] > ema_mid_slope.iloc[-2],
                ema_long_slope.iloc[-1] > ema_long_slope.iloc[-2]])

def decrease(data: DataFrame) -> bool:
    up_gradient, mid_gradient, low_gradient = data[MACD.UP_GRADIENT], data[MACD.MID_GRADIENT], data[MACD.LOW_GRADIENT]
    ema_up_slope, ema_mid_slope, ema_long_slope = data[EMA.SHORT_SLOPE], data[EMA.MID_SLOPE], data[EMA.LONG_SLOPE]
    return all([up_gradient.iloc[-1]  < up_gradient.iloc[-2],
                mid_gradient.iloc[-1] <  mid_gradient.iloc[-2],
                low_gradient.iloc[-1] <  low_gradient.iloc[-2],
                ema_up_slope.iloc[-1] <  0,
                ema_mid_slope.iloc[-1] < 0,
                ema_long_slope.iloc[-1] < 0])