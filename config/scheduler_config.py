import abc
class SchedulerConfig(abc.ABC):

    @abc.abstractmethod
    def start_scheduler(self):
        pass