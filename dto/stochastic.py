

class Stochastic:
    D_FAST = "Stochastic_D_FAST"
    D_SLOW = "Stochastic_D_SLOW"

    def __init__(self, data, k_len=10, k_smooth=6, d_smooth=6):
        low_price = data['low'].rolling(window=k_len, min_periods=1).min()
        high_price = data['high'].rolling(window=k_len, min_periods=1).max()
        k_fast = ((data["close"] - low_price) / (high_price - low_price)) * 100.0

        self.d_fast = k_fast.rolling(window=k_smooth, min_periods=1).mean()
        self.d_slow = self.d_fast.rolling(window=d_smooth, min_periods=1).mean()