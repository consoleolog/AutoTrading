import psycopg2
from sqlalchemy import create_engine

from config.scheduler_config import SchedulerConfig
from repository.candle_repository import CandleRepository
from service.trading_service import TradingService
from utils import database

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
        connection = psycopg2.connect(
            host=database.host,
            database=database.database,
            user=database.user,
            password=database.password,
            port=database.port,
        )
        db_url = f"postgresql://{database.user}:{database.password}@{database.host}:{database.port}/{database}"
        engine = create_engine(db_url)

        self.candle_repository = CandleRepository(connection, engine)
        self.trading_service = TradingService(
            ticker_list=ticker_list,
            candle_repository=self.candle_repository
        )

        self.scheduler_config = SchedulerConfig(
            trading_service=self.trading_service
        )