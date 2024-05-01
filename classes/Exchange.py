from abc import ABC, abstractmethod

class Exchange(ABC):
    @abstractmethod
    def new_buy_order(self, token_ticker, size):
        pass
    @abstractmethod
    def new_sell_oco_order(self, token_ticker, size, buyPrice, tp, sl):
        pass