import uuid
from apscheduler.schedulers.background import BackgroundScheduler

from config.scheduler_config import SchedulerConfig
from model.const.timeframe import TimeFrame
from service.trading_service import TradingService

class SchedulerConfigImpl(SchedulerConfig):
    def __init__(self, trading_service: TradingService):
        self._scheduler = BackgroundScheduler()
        self.trading_service = trading_service
        timeframe_keys = {
            TimeFrame.MINUTE_15: 15,
            TimeFrame.HALF_HOUR: 30,
            TimeFrame.HOUR: 60,
            TimeFrame.HOUR_4: 240
        }
        self._scheduler.add_job(
            func=trading_service.start_trading,
            trigger='interval',
            minutes=timeframe_keys[TimeFrame.HOUR],
            kwargs={
                "timeframe": TimeFrame.HOUR
            },
            id=f"{TimeFrame.HOUR}_{str(uuid.uuid4())}"
        )

    def start_scheduler(self):
        return self._scheduler.start()