import abc
import pandas as pd
import psycopg2
from logger import LoggerFactory

class IOrderRepository(abc.ABC):
    @abc.abstractmethod
    def find_by_ticker(self, ticker: str):
        pass
    @abc.abstractmethod
    def save(self, ticker, price, side):
        pass

class OrderRepository(IOrderRepository):
    def __init__(self, connection, engine):
        self.connection = connection
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        self.engine = engine

    def find_by_ticker(self, ticker:str):
        sql = """
        SELECT O.ORDER_ID,
               O.TICKER,
               O.PRICE,
               O.SIDE,
               O.CREATED_AT
        FROM BITHUMB_ORDER AS O
        WHERE O.TICKER = %(ticker)s
        AND O.SIDE = 'bid'
        ORDER BY O.CREATED_AT DESC
        LIMIT 1;
        """
        params = {"ticker": ticker}
        return pd.read_sql(sql, self.engine, params=params)

    def save(self, ticker, price, side):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                INSERT INTO BITHUMB_ORDER( 
                    TICKER,
                    PRICE,
                    SIDE
                ) VALUES (
                    %s,
                    %s,
                    %s
                )
                """, (ticker, price, side))
                self.connection.commit()
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()
