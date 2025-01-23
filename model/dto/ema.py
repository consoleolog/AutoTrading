from pandas import DataFrame

from logger import LoggerFactory
from model.const.stage import Stage

class EMA:
    SHORT = "EMA_SHORT"
    MID = "EMA_MIDDLE"
    LONG = "EMA_LONG"

    def __init__(self, data: DataFrame, period:int, column:str="close"):
        self.logger = LoggerFactory.get_logger(__class__.__name__, log_file="Model")
        self.val = data[column].ewm(span=period, adjust=False).mean()

    def get_stage(self, data: DataFrame)-> int:
        try:
            short, middle, long = data.iloc[-1][EMA.SHORT], data.iloc[-1][EMA.MID], data.iloc[-1][EMA.LONG]
            if short > middle > long:
                return Stage.STABLE_INCREASE
            elif middle > short > long:
                return Stage.END_OF_INCREASE
            elif middle > long > short:
                return Stage.START_OF_DECREASE
            elif long > middle > short:
                return Stage.STABLE_DECREASE
            elif long > short > middle:
                return Stage.END_OF_DECREASE
            elif short > long > middle:
                return Stage.START_OF_INCREASE
            else:
                return 0
        except IndexError as err:
            self.logger.warning(err)
            return 0