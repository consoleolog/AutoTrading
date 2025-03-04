import time
from concurrent.futures import ThreadPoolExecutor

import exchange
import utils
from constants import STAGE, TimeFrame
from mappers import ticker_position_mapper, ticker_status_mapper


def loop(tickers, timeframe):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(main, ticker, timeframe) for ticker in tickers]
        result = [f.result() for f in futures]
        format_time = time.strftime("%Y년 %m월 %d일 %H시 %M분 %S초", time.localtime())
        print(f"{format_time}\n{result}")


def calculate_profit(ticker, curr_price):
    status = ticker_status_mapper.find_by_ticker(ticker)
    buy_price = float(status.price)
    return ((curr_price - buy_price) / buy_price) * 100.0


def update_status(ticker):
    status = ticker_status_mapper.find_by_ticker(ticker)
    if status.side == "bid":
        price = (float(status.price) + exchange.get_current_price(ticker)) / 2
        ticker_status_mapper.update_one(ticker, price, "bid")
    else:
        ticker_status_mapper.update_one(
            ticker, exchange.get_current_price(ticker), "bid"
        )


def update_stochastic(ticker, k_slow, d_slow):
    """
    K 선과 D 선이 70 이상이면 True
    30 아래로 내려가면 모든 신호 초기화
    """
    if k_slow.iloc[-1] > 70 and d_slow.iloc[-1] > 70:
        ticker_position_mapper.update_stochastic(ticker, True)
    if k_slow.iloc[-1] < 30 and d_slow.iloc[-1] < 30:
        ticker_position_mapper.refresh(ticker)


def update_macd(ticker, golden_cross, dead_cross):
    """
    MACD 골든 크로스가 발생하면 True
    데드 크로스가 발생하면 False
    """
    if golden_cross.iloc[-2:].isin([True]).any():
        ticker_position_mapper.update_macd(ticker, True)
    if dead_cross.iloc[-2:].isin([True]).any():
        ticker_position_mapper.refresh(ticker)


def update_rsi(ticker, rsi):
    if rsi.iloc[-1] > rsi.iloc[-2] >= 50:
        ticker_position_mapper.update_rsi(ticker, True)
    if rsi.iloc[-1] > 70:
        ticker_position_mapper.refresh(ticker)


def main(ticker, timeframe):
    price_keys = {
        "BTC/KRW": 0.0002,
        "ETH/KRW": 0.0090,
        "BCH/KRW": 0.044,
        "AAVE/KRW": 0.030,
        "SOL/KRW": 0.08,
        "ENS/KRW": 1,
    }
    result = {}

    data = utils.create_sub_data(ticker, timeframe)
    K_SLOW, D_SLOW = utils.parse_data(data, returns=("K_SLOW", "D_SLOW"))
    update_stochastic(ticker, K_SLOW, D_SLOW)
    stage = utils.get_stage(data)
    result["basic_info"] = f"Ticker: {ticker} | Stage: {stage}"
    position = ticker_position_mapper.find_by_ticker(ticker)
    result["position"] = (
        f"RSI: {position.rsi} | MACD: {position.macd} | Stochastic: {position.stochastic}"
    )
    if position.stochastic:
        MACD_GoldenCross, MACD_DeadCross = utils.parse_data(
            data, returns=("MACD_GoldenCross", "MACD_DeadCross")
        )
        update_macd(ticker, MACD_GoldenCross, MACD_DeadCross)
        RSI = data["RSI"]
        update_rsi(ticker, RSI)

    if (
        position.stochastic
        and position.macd
        and position.macd.stochastic
        and stage
        in [STAGE.STABLE_DECREASE, STAGE.END_OF_DECREASE, STAGE.START_OF_INCREASE]
    ):
        update_status(ticker)
        ticker_position_mapper.refresh(ticker)
        exchange.create_buy_order(ticker, price_keys[ticker])

    balance = exchange.get_balance(ticker)
    if balance != 0:
        profit = calculate_profit(ticker, exchange.get_current_price(ticker))
        result["profit"] = profit
        Stochastic_DeadCross, MACD_DeadCross = utils.parse_data(
            data, returns=("Stochastic_DeadCross", "MACD_DeadCross")
        )
        if (
            profit < 0
            and (
                Stochastic_DeadCross.iloc[-2:].isin([True]).any()
                or Stochastic_DeadCross.iloc[-2:].isin([True]).any()
            )
            and stage == STAGE.STABLE_INCREASE
        ):
            ticker_position_mapper.refresh(ticker)
            ticker_status_mapper.update_one(
                ticker, exchange.get_current_price(ticker), "ask"
            )
            exchange.create_sell_order(ticker, balance)
            return result
        if (
            profit > 0.1
            and Stochastic_DeadCross.iloc[-2:].isin([True]).any()
            and stage
            in [STAGE.STABLE_INCREASE, STAGE.END_OF_INCREASE, STAGE.START_OF_DECREASE]
        ):
            ticker_position_mapper.refresh(ticker)
            ticker_status_mapper.update_one(
                ticker, exchange.get_current_price(ticker), "ask"
            )
            exchange.create_sell_order(ticker, balance)
            return result
        if profit > 0.1 and (
            Stochastic_DeadCross.iloc[-2:].isin([True]).any()
            or Stochastic_DeadCross.iloc[-2:].isin([True]).any()
        ):
            ticker_position_mapper.refresh(ticker)
            ticker_status_mapper.update_one(
                ticker, exchange.get_current_price(ticker), "ask"
            )
            exchange.create_sell_order(ticker, balance)
            return result
    return result
