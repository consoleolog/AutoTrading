class TickerStatus:
    def __init__(
        self,
        ticker=None,
        price=None,
        side=None,
        created_at=None,
        updated_at=None,
    ):
        self.ticker = ticker
        self.price = price
        self.side = side
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_df(df):
        ticker, price, side, created_at, updated_at = (
            df["ticker"],
            df["price"],
            df["side"],
            df["created_at"],
            df["updated_at"],
        )
        return TickerStatus(ticker, price, side, created_at, updated_at)
