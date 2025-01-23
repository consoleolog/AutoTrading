from contextlib import asynccontextmanager

from fastapi import FastAPI

from logger import LoggerFactory

logger = LoggerFactory.get_logger("server", "AutoTrading")

@asynccontextmanager
async def lifespan(app):
    logger.info("==================")
    logger.info("     START UP     ")
    logger.info("==================")
    yield

app = FastAPI(lifespan=lifespan)