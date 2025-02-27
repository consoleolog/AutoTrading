import pandas as pd
import abc
import psycopg2
from logger import LoggerFactory


class IStatusRepository(abc.ABC):
    @abc.abstractmethod
    def find_by_ticker(self, ticker: str):
        pass
    @abc.abstractmethod
    def save(self, ticker):
        pass
    @abc.abstractmethod
    def update_one(self, ticker, price, side):
        pass

class StatusRepository(IStatusRepository):
    def __init__(self, connection, engine):
        self.connection = connection
        self.logger = LoggerFactory.get_logger(__class__.__name__, "AutoTrading")
        self.engine = engine

    def find_by_ticker(self, ticker: str):
        sql = """
        SELECT S.TICKER,
               S.PRICE,
               S.SIDE,
               S.CREATED_AT,
               S.UPDATED_AT
        FROM BITHUMB_STATUS AS S 
        WHERE S.TICKER = %(ticker)s
        """
        params = {'ticker': ticker}
        data = pd.read_sql(sql, self.engine, params=params)
        return data.iloc[-1]

    def update_one(self, ticker, price, side):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE UPBIT_STATUS 
                    SET PRICE = %s,
                        SIDE = %s,
                        UPDATED_AT = NOW()
                    WHERE UPBIT_STATUS.TICKER = %s
                    """, (price, side, ticker)
                )
                self.connection.commit()
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()

    def save(self, ticker):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO BITHUMB_STATUS(TICKER)
                    VALUES (%s);
                    """,(ticker,)
                )
                self.connection.commit()
        except psycopg2.Error as e:
            self.logger.error(e)
            self.connection.rollback()
