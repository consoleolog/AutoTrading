import exchange
from constants import STAGE
from technical_indicator import EMA, MACD, RSI, Stochastic


def get_stage(data):
    """
    stage 1 (안정적인 상승)
    단 > 중 > 장
    stage 2 (상승의 끝)
    중 > 단 > 장
    stage 3 (하락의 시작)
    중 > 장 > 단
    stage 4 (안정적인 하락)
    장 > 중 > 단
    stage 5 (하락의 끝)
    장 > 단 > 중
    stage 6 (상승의 시작)
    단 > 장 > 중
    """
    EMA_SHORT, EMA_MIDDLE, EMA_LONG = (
        data["EMA_Short"].iloc[-1],
        data["EMA_Mid"].iloc[-1],
        data["EMA_Long"].iloc[-1],
    )
    if EMA_SHORT > EMA_MIDDLE > EMA_LONG:
        return STAGE.STABLE_INCREASE
    elif EMA_MIDDLE > EMA_SHORT > EMA_LONG:
        return STAGE.END_OF_INCREASE
    elif EMA_MIDDLE > EMA_LONG > EMA_SHORT:
        return STAGE.START_OF_DECREASE
    elif EMA_LONG > EMA_MIDDLE > EMA_SHORT:
        return STAGE.STABLE_DECREASE
    elif EMA_LONG > EMA_SHORT > EMA_MIDDLE:
        return STAGE.END_OF_DECREASE
    elif EMA_SHORT > EMA_LONG > EMA_MIDDLE:
        return STAGE.START_OF_INCREASE
    else:
        return 0


def parse_data(data, returns=("",)):
    return tuple(data[r] for r in returns)


def create_sub_data(ticker, timeframe, short_period=5, mid_period=20, long_period=40):
    data = exchange.get_candles(ticker, timeframe)

    # EMA
    data["EMA_Short"] = EMA(data["close"], short_period)
    data["EMA_Mid"] = EMA(data["close"], mid_period)
    data["EMA_Long"] = EMA(data["close"], long_period)

    # MACD
    (MACD_Value, MACD_Signal, MACD_Oscillator, MACD_GoldenCross, MACD_DeadCross) = MACD(
        data,
        10,
        20,
        returns=("value", "signal", "oscillator", "golden_cross", "dead_cross"),
    )
    data["MACD"] = MACD_Value
    data["MACD_Signal"] = MACD_Signal
    data["MACD_Oscillator"] = MACD_Oscillator
    data["MACD_GoldenCross"] = MACD_GoldenCross
    data["MACD_DeadCross"] = MACD_DeadCross

    # RSI
    (
        RSI_Value,
        RSI_Signal,
        RSI_GoldenCross,
        RSI_DeadCross,
    ) = RSI(data, returns=("value", "signal", "golden_cross", "dead_cross"))
    data["RSI"] = RSI_Value
    data["RSI_Signal"] = RSI_Signal
    data["RSI_GoldenCross"] = RSI_GoldenCross
    data["RSI_DeadCross"] = RSI_DeadCross

    # Stochastic
    (
        K_SLOW,
        D_SLOW,
        Stochastic_GoldenCross,
        Stochastic_DeadCross,
    ) = Stochastic(
        data, 14, 3, 3, returns=("k_slow", "d_slow", "golden_cross", "dead_cross")
    )
    data["K_SLOW"] = K_SLOW
    data["D_SLOW"] = D_SLOW
    data["Stochastic_GoldenCross"] = Stochastic_GoldenCross
    data["Stochastic_DeadCross"] = Stochastic_DeadCross

    return data
