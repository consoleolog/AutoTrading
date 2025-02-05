import uuid

from apscheduler.schedulers.background import BackgroundScheduler
from config.scheduler_config import SchedulerConfig
from model.const.timeframe import TimeFrame
from service.trading_service import TradingService

class SchedulerConfigImpl(SchedulerConfig):
    def __init__(self, trading_service: TradingService):
        self._scheduler = BackgroundScheduler()
        self.trading_service = trading_service

        # for timeframe in timeframes:
        self._scheduler.add_job(
            func=trading_service.start_trading,
            trigger='interval',
            minutes=TimeFrame.KEYS[TimeFrame.MINUTE_10],
            kwargs={
              "timeframe": TimeFrame.MINUTE_10
            },
            id=str(uuid.uuid4())
        )

    def start_scheduler(self):
        return self._scheduler.start()