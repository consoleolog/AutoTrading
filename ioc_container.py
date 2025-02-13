import inspect
import psycopg2
from typing import Any, Type, TypeVar
from sqlalchemy import create_engine
from scheduler import SchedulerConfig
from repository.candle_repository import ICandleRepository, CandleRepository
from repository.order_repository import IOrderRepository, OrderRepository
from trading_service import TradingService
from trading_service import ITradingService
import database

T = TypeVar('T')

class IocContainer:
    def __init__(self):
        self.obj_map = {}
        self.ticker_list = [
            "BTC/KRW",
            "ETH/KRW",
            "BCH/KRW",
            # "AAVE/KRW",
            # "SOL/KRW",
            # "BSV/KRW",
            # "YFI/KRW",
            # "BNB/KRW",
            # "COMP/KRW"
        ]

    def register(self, obj: Any):
        self.obj_map[type(obj)] = obj

    def get(self, type_: Type[T]) -> T:
        impl_type = type_
        if inspect.isabstract(type_):
            impl_type = type_.__subclasses__()
            if len(impl_type) == 0:
                raise ValueError("Can't Find Type")
            impl_type = impl_type[0]
        try:
            obj = self.obj_map[impl_type]
        except KeyError:
            raise ValueError("Can't Find Type")
        return obj

    def compose(self):

        connection = psycopg2.connect(
            host=database.host,
            database=database.database,
            user=database.user,
            password=database.password,
            port=database.port,
        )
        db_url = f"postgresql://{database.user}:{database.password}@{database.host}:{database.port}/{database.database}"
        engine = create_engine(db_url)
        self.register(CandleRepository(connection, engine))
        self.register(OrderRepository(connection, engine))
        self.register(TradingService(self.ticker_list, self.get(ICandleRepository), self.get(IOrderRepository)))
        self.register(SchedulerConfig(self.get(ITradingService)))