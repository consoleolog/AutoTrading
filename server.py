import time
import uuid
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from constants import TimeFrame
from main import loop

tickers = [
    "BTC/KRW",
    "ETH/KRW",
    "BCH/KRW",
    "ENS/KRW",
    "SOL/KRW",
    # "AAVE/KRW",
    # "BSV/KRW",
    # "YFI/KRW",
    # "BNB/KRW",
    # "COMP/KRW"
]

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=loop,
    trigger="interval",
    minutes=TimeFrame.KEYS[TimeFrame.MINUTE_10],
    kwargs={
        "timeframe": TimeFrame.MINUTE_15,
        "tickers": tickers,
    },
    id=str(uuid.uuid4()),
)


@asynccontextmanager
async def lifespan(app):
    format_time = time.strftime("%Y년 %m월 %d일 %H시 %M분 %S초", time.localtime())
    print(f"{format_time}\n==================")
    print("     START UP     ")
    print("==================")
    scheduler.start()
    yield


app = FastAPI(lifespan=lifespan)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
