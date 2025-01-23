from config.scheduler_config import SchedulerConfig
from repository.candle_repository import CandleRepository
from service.trading_service import TradingService
from utils.database import connection

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

        self.candle_repository = CandleRepository(connection)
        self.trading_service = TradingService(
            ticker_list=ticker_list,
            candle_repository=self.candle_repository
        )

        self.scheduler_config = SchedulerConfig(
            trading_service=self.trading_service
        )