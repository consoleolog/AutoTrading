import uuid
from apscheduler.schedulers.background import BackgroundScheduler

from config.scheduler_config import SchedulerConfig
from model.const.timeframe import TimeFrame
from service.trading_service import TradingService

class SchedulerConfigImpl(SchedulerConfig):
    def __init__(self, trading_service: TradingService):
        self._scheduler = BackgroundScheduler()
        self.trading_service = trading_service
        timeframes = [TimeFrame.HALF_HOUR, TimeFrame.HOUR]
        timeframe_keys = {
            TimeFrame.HALF_HOUR: 30,
            TimeFrame.HOUR: 60
        }
        for timeframe in timeframes:
            self._scheduler.add_job(
                func=trading_service.start_trading,
                trigger='interval',
                minutes=timeframe_keys[timeframe],
                kwargs={
                  "timeframe": timeframe
                },
                id=str(uuid.uuid4())
            )

    def start_scheduler(self):
        return self._scheduler.start()