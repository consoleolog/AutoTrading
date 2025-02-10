import abc
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import exchange
import utils
from dto.stochastic import Stochastic
from logger import LoggerFactory
from constant.stage import Stage
from constant.timeframe import TimeFrame
from dto.rsi import RSI
from entity.candle import Candle
from entity.candle_ema import CandleEMA
from entity.candle_macd import CandleMACD
from entity.order import Order
from repository.candle_repository import ICandleRepository
from repository.order_repository import IOrderRepository

class ITradingService(abc.ABC):
    @abc.abstractmethod
    def save_candle_data(self, ticker , timeframe: TimeFrame, data, stage: Stage)->Candle:
        pass
    @abc.abstractmethod
    def save_order_history(self, candle, response)->Order:
        pass
    @abc.abstractmethod
    def calculate_profit(self, ticker):
        pass
    @abc.abstractmethod
    def start_trading(self, timeframe: TimeFrame):
        pass
    @abc.abstractmethod
    def auto_trading(self, ticker:str, timeframe: TimeFrame):
        pass

class TradingService(ITradingService):
    def __init__(self,
                 ticker_list,
                 candle_repository: ICandleRepository,
                 order_repository: IOrderRepository,
                 ):
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        LoggerFactory.set_stream_level(LoggerFactory.INFO)
        self.ticker_list = ticker_list
        self.price_keys = {
            "BTC/KRW": 0.0002,
            "ETH/KRW": 0.0030,
            "BCH/KRW": 0.011,
            "AAVE/KRW": 0.015,
            "SOL/KRW": 0.02,
            "BSV/KRW": 0.1,
            "YFI/KRW": 0.0006,
            "BNB/KRW": 0.007,
            "COMP/KRW": 0.09,
        }
        self.candle_repository = candle_repository
        self.order_repository = order_repository

    def save_candle_data(self, ticker , timeframe: TimeFrame, data, stage: Stage)->Candle:
        try:
            candle = self.candle_repository.save_candle(
                Candle.of(str(uuid.uuid4()), datetime.now(), ticker, data["close"].iloc[-1], timeframe))
            candle_ema = self.candle_repository.save_candle_ema(CandleEMA.of(candle.candle_id, stage, data))
            self.candle_repository.save_candle_macd(CandleMACD.of(candle_ema.candle_id, data))
            return candle
        except Exception as e:
            self.logger.warning(e.__traceback__)
            pass
    def save_order_history(self, candle, response)-> Order:
        try:
            order = Order.of(candle, response, datetime.now())
            self.order_repository.save(order)
            return order
        except Exception as e:
            self.logger.warning(e.__traceback__)
            pass

    def calculate_profit(self, ticker):
        order_history = self.order_repository.find_by_ticker(ticker)
        current_price = exchange.get_current_price(ticker)
        buy_price = float(order_history["close"].iloc[-1])
        return (current_price - buy_price) / buy_price * 100.0

    def start_trading(self, timeframe: TimeFrame):
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.auto_trading, ticker, timeframe) for ticker in self.ticker_list]
            result = [f.result() for f in futures]
        self.logger.info(result)

    import os

    def auto_trading(self, ticker: str, timeframe: TimeFrame):
        result = {"ticker": ticker}
        stage, data = utils.get_data(ticker, timeframe, 5, 8, 13)
        filename = ticker.split("/")[0]
        balance = exchange.get_balance(ticker)

        # BUY
        if balance == 0:
            if stage in [Stage.STABLE_DECREASE, Stage.END_OF_DECREASE, Stage.START_OF_INCREASE]:
                position_path = f"{os.getcwd()}/{filename}_buy_position.txt"
                with open(position_path, "r") as position:
                    position_status = position.read().strip()

                fast, slow = data[Stochastic.D_FAST], data[Stochastic.D_SLOW]
                if position_status == "none" and fast.iloc[-1] < 25 and slow.iloc[-1] < 25:
                    with open(position_path, "w") as f:
                        f.write("stoch_check")

                rsi = data[RSI.RSI]
                if position_status == "stoch_check" and 45 <= rsi.iloc[-1] <= 55:
                    with open(position_path, "w") as f:
                        f.write("rsi_check")

                macd_bullish = utils.macd_bullish(data)
                if position_status == "rsi_check" and macd_bullish:
                    with open(position_path, "w") as f:
                        f.write("macd_check")

                if position_status == "macd_check" and fast.iloc[-1] < 70:
                    exchange.create_buy_order(ticker, self.price_keys[ticker])
                    with open(position_path, "w") as f:
                        f.write(str(data["close"].iloc[-1]))  # 매수가 저장
                else:
                    with open(position_path, "w") as f:
                        f.write("none")

        # SELL
        else:
            position_path = f"{os.getcwd()}/{filename}_sell_position.txt"
            with open(position_path, "r") as position:
                position_status = position.read().strip()

            with open(f"{os.getcwd()}/{filename}_buy_position.txt", "r") as f:
                entry_price = f.read().strip()

            try:
                entry_price = float(entry_price)
            except ValueError:
                entry_price = None

            if entry_price:
                stop_loss = entry_price * 0.95  # 예: 5% 손절
                take_profit = entry_price + (entry_price - stop_loss) * 1.5  # 손절폭 * 1.5만큼 익절 설정

                if data["close"].iloc[-1] > take_profit:
                    exchange.create_sell_order(ticker, balance)
                    with open(position_path, "w") as f:
                        f.write("none")
                if position_status == "sell":
                    sell_price = min(data["close"].iloc[-10:].max(), take_profit)  # 익절 구간 적용
                    if data["close"].iloc[-1] > sell_price:
                        exchange.create_sell_order(ticker, balance)
                        with open(position_path, "w") as f:
                            f.write("none")

            fast, slow = data[Stochastic.D_FAST], data[Stochastic.D_SLOW]
            if position_status == "none" and fast.iloc[-1] > 70 and slow.iloc[-1] > 70:
                with open(position_path, "w") as f:
                    f.write("stoch_check")

            rsi = data[RSI.RSI]
            if position_status == "stoch_check" and 45 <= rsi.iloc[-1] <= 70:
                with open(position_path, "w") as f:
                    f.write("rsi_check")

            macd_bearish = utils.macd_bearish(data)
            if position_status == "rsi_check" and macd_bearish:
                with open(position_path, "w") as f:
                    f.write("macd_check")

            if position_status == "macd_check" and fast.iloc[-1] > 30:
                with open(position_path, "w") as f:
                    f.write("sell")

        return result
