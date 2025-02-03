import abc

from model.entity.order import Order


class OrderRepository(abc.ABC):

    @abc.abstractmethod
    def find_all(self):
        pass
    @abc.abstractmethod
    def find_by_ticker(self, ticker: str):
        pass
    @abc.abstractmethod
    def save(self, order: Order)->Order:
        pass