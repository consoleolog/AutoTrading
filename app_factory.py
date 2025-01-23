from config.scheduler_config import SchedulerConfig
from service.trading_service import TradingService


class AppFactory:
    def __init__(self):
        ticker_list = [
            "BTC/KRW",
            "ETH/KRW",
            "BCH/KRW",
            "AAVE/KRW",
            "SOL/KRW",
            "BSV/KRW",
            "YFI/KRW",
            "BNB/KRW",
            "COMP/KRW"
        ]
        self.trading_service = TradingService(ticker_list)
        self.scheduler_config = SchedulerConfig(
            trading_service=self.trading_service
        )