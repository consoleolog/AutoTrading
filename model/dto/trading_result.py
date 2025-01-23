
class TradingResult:
    def __init__(self, trading_result: dict):
        self.ticker = trading_result['ticker']
        self.mode = trading_result['mode']
        self.peekout = trading_result['peekout']
        self.cross_signal = trading_result['cross_signal']
        if trading_result['increase'] is not None:
            self.increase = trading_result['increase']
        if trading_result['decrease'] is not None:
            self.decrease = trading_result['decrease']

    def __str__(self):
        return f"""
        TradingResult(
        ticker: {self.ticker},
        mode: {self.mode},
        peekout: {self.peekout},
        increase: {self.increase},
        decrease: {self.decrease}
        cross_signal: {self.cross_signal},
        )
        """