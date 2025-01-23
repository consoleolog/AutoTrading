
class TickerInfo:
    def __init__(
            self,
            ask = None,
            ask_volume = None,
            average = None,
            base_volume = None,
            bid = None,
            bid_volume = None,
            change = None,
            close = None,
            datetime = None,
            high = None,
            info = None,
            last = None,
            low = None,
            open = None,
            percentage = None,
            previous_close = None,
            quote_volume = None,
            symbol = None,
            timestamp = None,
            vwap = None,
    ):
        self.ask = ask
        self.ask_volume = ask_volume
        self.average = average
        self.base_volume = base_volume
        self.bid = bid
        self.bid_volume = bid_volume
        self.change = change
        self.close = close
        self.datetime = datetime
        self.high = high
        self.info = info
        self.last = last
        self.low = low
        self.open = open
        self.percentage = percentage
        self.previous_close = previous_close
        self.quote_volume = quote_volume
        self.symbol = symbol
        self.timestamp = timestamp
        self.vwap = vwap

    @staticmethod
    def from_dict(dicts):
        return TickerInfo(
            ask = dicts['ask'],
            ask_volume = dicts['askVolume'],
            average = dicts['average'],
            base_volume = dicts['baseVolume'],
            bid = dicts['bid'],
            bid_volume = dicts['bidVolume'],
            change = dicts['change'],
            close = dicts['close'],
            datetime = dicts['datetime'],
            high = dicts['high'],
            info = dicts['info'],
            last = dicts['last'],
            low = dicts['low'],
            open = dicts['open'],
            percentage = dicts['percentage'],
            previous_close = dicts['previousClose'],
            quote_volume = dicts['quoteVolume'],
            symbol = dicts['symbol'],
            timestamp = dicts['timestamp'],
            vwap = dicts['vwap'],
        )


    def __str__(self):
        return f"""
        TickerInfo(
            ask = {self.ask},
            ask_volume = {self.ask_volume},
            average = {self.average},
            base_volume = {self.base_volume},
            bid = {self.bid},
            bid_volume = {self.bid_volume},
            change = {self.change},
            close = {self.close},
            datetime = {self.datetime},
            high = {self.high},
            info = {self.info},
            last = {self.last},
            low = {self.low},
            open = {self.open},
            percentage = {self.percentage},
            previous_close = {self.previous_close},
            quote_volume = {self.quote_volume},
            symbol = {self.symbol},
            timestamp = {self.timestamp},
            vwap = {self.vwap},
        )"""