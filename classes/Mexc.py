import time
from mexc_api.spot import Spot
from classes.Exchange import Exchange

class Mexc(Exchange):
    def __init__(self):
        self.oco_timeout = 120
        self.client = Spot()

    def __get_price(self, token_ticker):
        return self.client.market.ticker_price(token_ticker)

    def new_buy_order(self, token_ticker, size):
        return self.client.account.new_order(token_ticker + 'USDT', 'buy', size=size)
    
    def new_sell_oco_order(self, token_ticker, size, buyPrice, tp, sl):
        for i in range(0, self.oco_timeout):
            token_price = self.__get_price(token_ticker)
            if (token_price < buyPrice - buyPrice*sl) or (token_price > buyPrice + buyPrice*tp) or (i == self.oco_timeout-1):
                return self.client.account.new_order(token_ticker + '-USDT', 'sell', size=size)
            time.sleep(1)