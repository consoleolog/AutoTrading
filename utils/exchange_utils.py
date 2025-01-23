import os
import ccxt
import pandas as pd
from dotenv import load_dotenv
from model.const.timeframe import TimeFrame
from model.dto.ticker_info import TickerInfo
load_dotenv()
exchange = getattr(ccxt, os.getenv("ID"))({
    'apiKey': os.getenv("ACCESS_KEY"),
    'secret': os.getenv("SECRET_KEY")
})

def get_ticker_info(ticker:str) -> TickerInfo:
    tickers = exchange.fetch_tickers()
    info = tickers[ticker]
    return TickerInfo.from_dict(info)

def get_krw() -> float:
    balances = exchange.fetch_balance()
    krw = balances["KRW"]
    return float(krw["free"])

def create_buy_order(ticker:str, amount: float):
    return exchange.create_market_buy_order(
        symbol=ticker,
        amount=amount
    )

def create_sell_order(ticker:str, amount: float):
    return exchange.create_market_sell_order(
        symbol=ticker,
        amount=amount
    )

def get_current_price(ticker:str)->float:
    ticker_info = get_ticker_info(ticker)
    return float(ticker_info.close)

def get_avg_buy_price(ticker:str)->float:
    ticker_info = get_ticker_info(ticker)
    return float(ticker_info.average)

def get_profit(ticker:str)->float:
    current_price = get_current_price(ticker)
    avg_buy_price = get_avg_buy_price(ticker)
    return (current_price - avg_buy_price) / avg_buy_price * 100.0

def get_balance(ticker: str) -> float:
    format_ticker = ticker.replace("/KRW", "")
    balances = exchange.fetch_balance()
    balance = balances[format_ticker]
    return float(balance['free'])

def get_candles(ticker, timeframe: TimeFrame) -> pd.DataFrame:
    ohlcv = exchange.fetch_ohlcv(symbol=ticker, timeframe=timeframe)
    df = pd.DataFrame(ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    pd_ts = pd.to_datetime(df['datetime'], utc=True, unit='ms')
    pd_ts = pd_ts.dt.tz_convert("Asia/Seoul")
    pd_ts = pd_ts.dt.tz_localize(None)
    df.set_index(pd_ts, inplace=True)
    df = df[['datetime','close']]
    return df