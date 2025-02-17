import utils
from contextlib import asynccontextmanager
from fastapi import FastAPI
from scheduler import ISchedulerConfig
from ioc_container import IocContainer
from logger import LoggerFactory

logger = LoggerFactory.get_logger("server", "AutoTrading")
container = IocContainer()

@asynccontextmanager
async def lifespan(app):
    logger.info("==================")
    logger.info("     START UP     ")
    logger.info("==================")
    container.compose()
    scheduler_config = container.get(ISchedulerConfig)
    scheduler_config.start_scheduler()
    yield
app = FastAPI(lifespan=lifespan)