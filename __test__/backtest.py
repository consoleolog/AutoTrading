from backtesting import Strategy, Backtest
import sys, os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from dto.stochastic import Stochastic
from dto.ema import EMA
import utils
from constant.stage import Stage
from constant.timeframe import TimeFrame
from dto.macd import MACD
from dto.rsi import RSI
from logger import LoggerFactory

logger = LoggerFactory().get_logger(__name__)
LoggerFactory.set_stream_level(LoggerFactory.DEBUG)

class MyStrategy(Strategy):
    def __init__(self, broker, data, params):
        super().__init__(broker, data, params)
        self.logger = None

    def init(self):
        self.info = {
            "position": "long",
            "stoch": False,
            "rsi": False,
            "macd": False
        }
        self.logger = logger

    def next(self):
        df = self.data.df
        stage = EMA.get_stage(df)
        fast, slow = df[Stochastic.D_FAST].iloc[-1], df[Stochastic.D_SLOW].iloc[-1]

        rsi, rsi_sig = df[RSI.LONG].iloc[-1], df[RSI.LONG_SIG].iloc[-1]
        if self.position:
            if self.position.pl_pct > 0.01:
                self.logger.debug(self.position.pl_pct)
                self.position.close()
            # if df[MACD.LONG_BEARISH].iloc[-2:].isin([True]).any() and stage in [Stage.STABLE_INCREASE, Stage.END_OF_INCREASE, Stage.START_OF_DECREASE]:
            #     self.position.close()
            # if df[MACD.SHORT_BEARISH].iloc[-2:].isin([True]).any():
            #     self.position.close()
        else:

            if stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.START_OF_INCREASE]:
                if df[MACD.SHORT_BULLISH].iloc[-2:].isin([True]).any() and rsi <= 40:
                    self.buy()


ticker = "ENS/KRW"
timeframe = TimeFrame.MINUTE_3

_, data = utils.get_data(ticker, timeframe, 5, 8, 13)
data = data.rename(columns={
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume"
})

bt = Backtest(
    data=data[:-50],
    strategy=MyStrategy,
    cash=1000000000000,
    # commission=0.0004,
)
#  0.001   0.1
#  0.0004  0.04
results = bt.run()
logger.info(results)
# bt.plot()