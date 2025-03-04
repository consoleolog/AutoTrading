import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine

from models.ticker_position import TickerPosition

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
            INSERT INTO BITHUMB_POSITION(TICKER)
            VALUES(%s)
            """,
            (ticker,),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()


def find_by_ticker(ticker):
    data = pd.read_sql(
        """
        SELECT P.TICKER,
               P.RSI,
               P.MACD,
               P.STOCHASTIC,
               P.CREATED_AT,
               P.UPDATED_AT 
        FROM BITHUMB_POSITION AS P 
        WHERE P.TICKER = %(ticker)s
        """,
        engine,
        params={"ticker": ticker},
    )
    return TickerPosition.from_df(data.iloc[-1])


def update_rsi(ticker, rsi):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE BITHUMB_POSITION
            SET RSI = %s, 
                UPDATED_AT = NOW()
            WHERE BITHUMB_POSITION.TICKER = %s
            """,
            (rsi, ticker),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()


def update_macd(ticker, macd):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE BITHUMB_POSITION
            SET MACD = %s,
                UPDATED_AT = NOW()
            WHERE BITHUMB_POSITION.TICKER = %s
            """,
            (macd, ticker),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()


def update_stochastic(ticker, stochastic):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE BITHUMB_POSITION
            SET STOCHASTIC = %s,
                UPDATED_AT = NOW()
            WHERE BITHUMB_POSITION.TICKER = %s
            """,
            (stochastic, ticker),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()


def refresh(ticker):
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE BITHUMB_POSITION
            SET RSI = %s,
                MACD = %s,
                STOCHASTIC = %s,
                UPDATED_AT = NOW()
            WHERE BITHUMB_POSITION.TICKER = %s
            """,
            (False, False, False, ticker),
        )
        conn.commit()
        cur.close()
    except psycopg2.Error:
        conn.rollback()
