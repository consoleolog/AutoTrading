from datetime import datetime

from entity.candle import Candle


class Order:
    def __init__(
        self,
        order_id: str = None,
        candle_id: str = None,
        ticker: str = None,
        close: float = None,
        mode:str = None,
        created_at: datetime = None,
    ):
        self.order_id = order_id
        self.candle_id = candle_id
        self.ticker = ticker
        self.close = close
        self.mode = mode
        self.created_at = created_at

    @staticmethod
    def of(candle:Candle, response:dict, created_at:datetime):
        return Order(
            order_id=response["id"],
            candle_id=candle.candle_id,
            close=candle.close,
            mode=response["side"],
            ticker=response["symbol"],
            created_at=created_at
        )

    def __str__(self):
        return f"""
        Order(
            order_id: {self.order_id},
            candle_id: {self.candle_id},
            ticker: {self.ticker},
            close: {self.close},
            mode: {self.mode},
            created_at: {self.created_at}
        )"""