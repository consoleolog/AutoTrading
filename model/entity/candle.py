from datetime import datetime
from model.const.timeframe import TimeFrame

class Candle:
    def __init__(
        self,
        candle_id: str = None,
        create_at: datetime = datetime.now(),
        ticker: str = None,
        close: float = None,
        timeframe: TimeFrame = None,
    ):
        self.candle_id = candle_id
        self.create_at = create_at
        self.ticker = ticker
        self.close = close
        self.timeframe = timeframe

    @staticmethod
    def of(candle_id:str, create_at: datetime, ticker:str, close:float, timeframe:TimeFrame):
        return Candle(
            candle_id=candle_id,
            create_at=create_at,
            ticker=ticker,
            close=float(close),
            timeframe=timeframe,
        )

    def __str__(self):
        return f"""
        Candle(
            candle_id={self.candle_id},
            create_at={self.create_at},
            ticker={self.ticker},
            close={self.close},
            timeframe={self.timeframe}
        )"""