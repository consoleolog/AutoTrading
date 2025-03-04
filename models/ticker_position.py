class TickerPosition:
    def __init__(
        self,
        ticker=None,
        macd=None,
        rsi=None,
        stochastic=None,
        created_at=None,
        updated_at=None,
    ):
        self.ticker = ticker
        self.macd = macd
        self.rsi = rsi
        self.stochastic = stochastic
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def from_df(df):
        ticker, macd, rsi, stochastic, created_at, updated_at = (
            df["ticker"],
            df["macd"],
            df["rsi"],
            df["stochastic"],
            df["created_at"],
            df["updated_at"],
        )
        return TickerPosition(ticker, macd, rsi, stochastic, created_at, updated_at)
