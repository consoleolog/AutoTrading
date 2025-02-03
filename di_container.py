import inspect
import psycopg2
from typing import Any, Type, TypeVar
from sqlalchemy import create_engine
from config.impl.scheduler_config_impl import SchedulerConfigImpl
from repository.candle_repository import CandleRepository
from repository.impl.candle_repository_impl import CandleRepositoryImpl
from repository.impl.order_repository_impl import OrderRepositoryImpl
from repository.order_repository import OrderRepository
from service.impl.trading_service_impl import TradingServiceImpl
from service.trading_service import TradingService
from utils import database
from utils.exception.not_registered_exception import NotRegisteredException

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
                raise NotRegisteredException(impl_type, "Can't Find Type")
            impl_type = impl_type[0]
        try:
            obj = self.obj_map[impl_type]
        except KeyError:
            raise NotRegisteredException(impl_type, "Can't Find Type")
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
        db_url = f"postgresql://{database.user}:{database.password}@{database.host}:{database.port}/{database.database}"
        engine = create_engine(db_url)
        self.register(CandleRepositoryImpl(connection, engine))
        self.register(OrderRepositoryImpl(connection, engine))
        self.register(TradingServiceImpl(ticker_list, self.get(CandleRepository), self.get(OrderRepository)))
        self.register(SchedulerConfigImpl(self.get(TradingService)))