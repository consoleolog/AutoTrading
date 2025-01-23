from contextlib import asynccontextmanager
from fastapi import FastAPI
from app_factory import AppFactory
from logger import LoggerFactory

logger = LoggerFactory.get_logger("server", "AutoTrading")
app_factory = AppFactory()
scheduler_config = app_factory.scheduler_config

@asynccontextmanager
async def lifespan(app):
    logger.info("==================")
    logger.info("     START UP     ")
    logger.info("==================")
    scheduler_config.start_scheduler()
    yield
app = FastAPI(lifespan=lifespan)