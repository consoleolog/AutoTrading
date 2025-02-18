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
        else:

            if stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.START_OF_INCREASE]:
                bullish = all([
                    df[MACD.SHORT_BULLISH].iloc[-2:].isin([True]).any(),
                ])
                peek_out = all([
                    df[MACD.SHORT_HIST].iloc[-1] > df[MACD.SHORT_HIST].iloc[-8:].min(),
                    df[MACD.LONG_HIST].iloc[-1] > df[MACD.LONG_HIST].iloc[-8:].min(),
                ])
                if  peek_out and rsi <= 40:
                    # self.logger.debug(df)
                    self.buy()


ticker = "BCH/KRW"
timeframe = TimeFrame.MINUTE_15

_, data = utils.get_data(ticker, timeframe, 5, 8, 13)
data = data.rename(columns={
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume"
})
unique_days = sorted(data.index.normalize().unique())

if len(unique_days) < 2:
    raise ValueError("데이터에 2일치 이상의 데이터가 필요합니다.")

two_days = unique_days[-1:]

data_two_days = data[data.index.normalize().isin(two_days)]

bt = Backtest(
    data=data_two_days,
    strategy=MyStrategy,
    cash=1000000000000,
    commission=0.0004,
)
#  0.001   0.1
#  0.0004  0.04
results = bt.run()
logger.info(results)
# bt.plot()