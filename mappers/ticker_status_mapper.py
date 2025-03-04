import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine

from models import TickerStatus

load_dotenv()
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")
db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
engine = create_engine(db_url)
conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
    port=port,
)


def init(ticker):
    cur = conn.cursor()
    try:
        cur.execute(
            """
             INSERT INTO BITHUMB_STATUS(TICKER)
             VALUES(%s)
             """,
            (ticker,),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()


def update_one(ticker, price, side):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE BITHUMB_STATUS
            SET PRICE = %s,
                SIDE = %s,
                UPDATED_AT = NOW()
            WHERE BITHUMB_STATUS.TICKER = %s
            """,
            (price, side, ticker),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()


def find_by_ticker(ticker):
    data = pd.read_sql(
        """
        SELECT S.TICKER,
               S.PRICE,
               S.SIDE,
               S.CREATED_AT,
               S.UPDATED_AT
        FROM BITHUMB_STATUS AS S 
        WHERE S.TICKER = %(ticker)s
        """,
        engine,
        params={"ticker": ticker},
    )
    return TickerStatus.from_df(data.iloc[-1])
