from pandas import DataFrame

from model.dto.macd import MACD


class Histogram:
    UP = "UP_HISTOGRAM"
    MID = "MID_HISTOGRAM"
    LOW = "LOW_HISTOGRAM"

    def __init__(self, data: DataFrame):
        self.up_val = data[MACD.UP] - data[MACD.UP_SIGNAL]
        self.mid_val = data[MACD.MID] - data[MACD.MID_SIGNAL]
        self.low_val = data[MACD.LOW] - data[MACD.LOW_SIGNAL]