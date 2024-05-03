from abc import ABC, abstractmethod

class Exchange(ABC):
    @abstractmethod
    def new_buy_order(self, token_ticker: str, size: str):
        pass
    @abstractmethod
    def new_sell_oco_order(self, token_ticker: str, size: str, buy_price: float, tp: float, sl: float):
        pass