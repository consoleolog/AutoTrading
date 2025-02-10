import abc
import pandas as pd
import psycopg2
from logger import LoggerFactory
from entity.order import Order

class IOrderRepository(abc.ABC):
    @abc.abstractmethod
    def find_all(self):
        pass
    @abc.abstractmethod
    def find_by_ticker(self, ticker: str):
        pass
    @abc.abstractmethod
    def save(self, order: Order)->Order:
        pass

class OrderRepository(IOrderRepository):
    def __init__(self, connection, engine):
        self.connection = connection
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        self.engine = engine

    def find_all(self):
        sql = """SELECT O.ORDER_ID, 
                        O.CANDLE_ID,
                        O.TICKER,
                        O.CLOSE,
                        O.MODE,
                        O.CREATED_AT 
                 FROM ORDER_HISTORY AS O
                 ORDER BY O.CREATED_AT DESC"""
        return pd.read_sql(sql, self.engine)

    def find_by_ticker(self, ticker:str):
        sql = """SELECT O.ORDER_ID, 
                        O.CANDLE_ID,
                        O.TICKER,
                        O.CLOSE,
                        O.MODE,
                        O.CREATED_AT 
                 FROM ORDER_HISTORY AS O
                 WHERE O.TICKER = %(ticker)s
                 ORDER BY O.CREATED_AT DESC
                 LIMIT 1
                 """
        params = {"ticker": ticker}
        return pd.read_sql(sql, self.engine, params=params)

    def save(self, order: Order):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO ORDER_HISTORY( 
                    ORDER_ID,
                    CANDLE_ID,
                    TICKER,
                    CLOSE,
                    MODE,
                    CREATED_AT
                ) VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """, (
                    order.order_id,
                    order.candle_id,
                    order.ticker,
                    order.close,
                    order.mode,
                    order.created_at
                ))
                self.connection.commit()
                return order
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()
