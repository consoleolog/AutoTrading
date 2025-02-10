import os

from backtesting import Backtest, Strategy
import utils
from constant.stage import Stage
from constant.timeframe import TimeFrame
from dto.ema import EMA
from dto.rsi import RSI
from dto.stochastic import Stochastic

class MyStrategy(Strategy):
    def init(self):
        pass

    def next(self):
        ticker = "BTC/KRW"
        df = self.data.df
        filename = "BTC"
        stage = EMA.get_stage(df)
        if stage == Stage.STABLE_DECREASE or stage == Stage.END_OF_DECREASE or stage == Stage.START_OF_INCREASE:
            position = open(f"{os.getcwd()}/{filename}_buy_position.txt", "r")
            fast, slow = data[Stochastic.D_FAST], data[Stochastic.D_SLOW]
            if position.read() == "none" and fast.iloc[-1] < 25 and slow.iloc[-1] < 25:
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write("over_sell")
            rsi = data[RSI.RSI]
            if position.read() == "over_sell" and 45 <= rsi.iloc[-1] <= 55:
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write("rsi_check")
            else:
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write("none")
            macd_bullish = utils.macd_bullish(data)
            if position.read() == "rsi_check" and macd_bullish:
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write("macd_check")
            else:
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write("none")
            if position.read() == "macd_check" and fast.iloc[-1] < 65:
                self.buy()
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write(data["close"].iloc[-1])
            else:
                with open(f"{os.getcwd()}/{filename}_buy_position.txt", "w") as f:
                    f.write("none")

ticker = "BTC/KRW"
position_file = f"{os.getcwd()}/BTC_buy_position.txt"

if not os.path.exists(position_file):
    with open(position_file, "w") as f:
        f.write("none")
stage, data = utils.get_data("BTC/KRW", TimeFrame.MINUTE_3, 5, 8, 13)
data = data.rename(columns={"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"})

bt = Backtest(
    data=data,
    strategy=MyStrategy,
    cash=10000000,  # 초기 현금을 늘려서 매매 가능하게 조정
    commission=0.002,
    trade_on_close=True
)

# 결과 실행 및 시각화
results = bt.run()
print(results)
bt.plot()
