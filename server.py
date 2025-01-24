from contextlib import asynccontextmanager
from fastapi import FastAPI
from config.scheduler_config import SchedulerConfig
from di_container import DIContainer
from logger import LoggerFactory

logger = LoggerFactory.get_logger("server", "AutoTrading")
container = DIContainer()

@asynccontextmanager
async def lifespan(app):
    logger.info("==================")
    logger.info("     START UP     ")
    logger.info("==================")
    container.compose()
    scheduler_config = container.get(SchedulerConfig)
    scheduler_config.start_scheduler()
    yield
app = FastAPI(lifespan=lifespan)