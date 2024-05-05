from abc import ABC, abstractmethod

class Exchange(ABC):
    @abstractmethod
    def new_buy_order(self, token_ticker: str, size: str):
        """
        :param token_ticker: a valid trading symbol code
        :param size: size of the quoted token to buy
        :return: bought token amount
        """
        pass
    @abstractmethod
    def new_sell_tp_sl_order(self, token_ticker: str, size: str, buy_price: float, tp: float, sl: float):
        """
        :param token_ticker: a valid trading symbol code
        :param size: amount of base tokens to sell
        :buy_price: bought token price
        :tp: take profit
        :sl: stop loss
        :return: generated profit from the trade
        """
        pass