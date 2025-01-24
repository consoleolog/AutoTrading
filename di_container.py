import inspect
from typing import Any, Type, TypeVar
import psycopg2
from sqlalchemy import create_engine
from config.scheduler_config import SchedulerConfig
from repository.candle_repository import CandleRepository
from service.trading_service import TradingService
from utils import database

T = TypeVar('T')

class DIContainer:
    def __init__(self):
        self.obj_map = {}

    def register(self, obj: Any):
        self.obj_map[type(obj)] = obj

    def get(self, type_: Type[T]) -> T:
        impl_type = type_
        if inspect.isabstract(type_):
            impl_type = type_.__subclasses__()
            if len(impl_type) == 0:
                raise ValueError()
            impl_type = impl_type[0]
        try:
            obj = self.obj_map[impl_type]
        except KeyError:
            raise TypeError()
        return obj

    def compose(self):
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
        self.register(CandleRepository(connection, engine))
        self.register(TradingService(ticker_list, self.get(CandleRepository)))
        self.register(SchedulerConfig(self.get(TradingService)))