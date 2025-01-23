import os

import ccxt
import pandas as pd
from dotenv import load_dotenv
from typing import Optional
from logger import LoggerFactory
from model.const.timeframe import TimeFrame
from model.dto.ticker_info import TickerInfo

load_dotenv()

logger = LoggerFactory().get_logger("exchange_utils", "AutoTrading")

exchange = getattr(ccxt, os.getenv("ID"))({
    'apiKey': os.getenv("ACCESS_KEY"),
    'secret': os.getenv("SECRET_KEY")
})

def get_ticker_info(ticker:str) -> Optional[TickerInfo]:
    try:
        tickers = exchange.fetch_ticker(ticker)
        info = tickers[ticker]
        return TickerInfo.from_dict(info)
    except Exception as e:
        logger.error(f"Error With {ticker} - {str(e)}")
        return None

def get_krw() -> Optional[float]:
    try:
        balances = exchange.fetch_balance()
        krw = balances["KRW"]
        return float(krw["free"])
    except Exception as e:
        logger.error(f"Error With get Krw- {str(e)}")
        return None

def create_buy_order(ticker:str, amount: float):
    try:
        return exchange.create_market_buy_order(
            symbol=ticker,
            amount=amount
        )
    except Exception as e:
        logger.error(f"Error With CreateBuyOrder {ticker} - {str(e)}")
        return None

def create_sell_order(ticker:str, amount: float):
    try:
        return exchange.create_market_sell_order(
            symbol=ticker,
            amount=amount
        )
    except Exception as e:
        logger.error(f"Error With CreateSellOrder {ticker} - {str(e)}")
        return None

def get_current_price(ticker:str)->Optional[float]:
    try:
        ticker_info = get_ticker_info(ticker)
        return float(ticker_info.close)
    except Exception as e:
        logger.error(f"Error With Get CurrentPrice {ticker} - {str(e)}")
        return None

def get_avg_buy_price(ticker:str)->Optional[float]:
    try:
        ticker_info = get_ticker_info(ticker)
        return float(ticker_info.average)
    except Exception as e:
        logger.error(f"Error With Get AveragePrice {ticker} - {str(e)}")
        return None

def get_profit(ticker:str)->Optional[float]:
    current_price = get_current_price(ticker)
    avg_buy_price = get_avg_buy_price(ticker)
    if avg_buy_price is not None and current_price is not None:
        return (current_price - avg_buy_price) / avg_buy_price * 100.0
    else:
        return None

def get_balance(ticker: str) -> float:
    format_ticker = ticker.replace("/KRW", "")
    balances = exchange.fetch_balance()
    try:
        balance = balances[format_ticker]
        if balance == 0:
            return 0
        return float(balance['free'])
    except KeyError:
        return 0

def get_candles(self, ticker, timeframe: TimeFrame) -> pd.DataFrame:
    ohlcv = self.exchange.fetch_ohlcv(symbol=ticker, timeframe=timeframe)
    df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
    pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
    pd_ts = pd_ts.dt.tz_localize(None)
    df.set_index(pd_ts, inplace=True)
    df = df[['datetime','close']]
    return df