

class Stochastic:
    D_FAST = "Stochastic_D_FAST"
    D_SLOW = "Stochastic_D_SLOW"

    BULLISH = "Stochastic_BULLISH"
    BEARISH = "Stochastic_BEARISH"

    OVER_BOUGHT = 75
    OVER_SOLD = 25

    def __init__(self, data, k_len=10, k_smooth=6, d_smooth=6):
        low_price = data['low'].rolling(window=k_len, min_periods=1).min()
        high_price = data['high'].rolling(window=k_len, min_periods=1).max()
        k_fast = ((data["close"] - low_price) / (high_price - low_price)) * 100.0

        self.d_fast = k_fast.rolling(window=k_smooth, min_periods=1).mean()
        self.d_slow = self.d_fast.rolling(window=d_smooth, min_periods=1).mean()
        self.bullish_val = (self.d_fast.shift(1) < self.d_slow.shift(1)) & (self.d_fast > self.d_slow)
        self.bearish_val = (self.d_fast.shift(1) > self.d_slow.shift(1)) & (self.d_fast < self.d_slow)
