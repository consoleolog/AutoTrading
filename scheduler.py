import abc
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from constant.timeframe import TimeFrame
from trading_service import ITradingService


class ISchedulerConfig(abc.ABC):
    @abc.abstractmethod
    def start_scheduler(self):
        pass

class SchedulerConfig(ISchedulerConfig):
    def __init__(self, trading_service: ITradingService):
        self._scheduler = BackgroundScheduler()
        self.trading_service = trading_service

        # for timeframe in timeframes:
        self._scheduler.add_job(
            func=trading_service.start_trading,
            trigger='interval',
            minutes=TimeFrame.KEYS[TimeFrame.MINUTE_3],
            kwargs={
              "timeframe": TimeFrame.MINUTE_3,
            },
            id=str(uuid.uuid4())
        )

    def start_scheduler(self):
        return self._scheduler.start()