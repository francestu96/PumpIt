from kucoin.client import Trade
from classes.Exchange import Exchange

class Kucoin(Exchange):
    def __init__(self):
        self.client = Trade()

    def new_buy_order(self, token_ticker, size):
        return self.client.create_market_order(token_ticker + '-USDT', 'buy', size=size)
    
    def new_sell_oco_order(self, token_ticker, size, buyPrice, tp, sl):
        return self.client.create_oco_order(
            token_ticker + '-USDT', 
            'sell', 
            price=(buyPrice + buyPrice*tp), 
            stopPrice=(buyPrice - buyPrice*sl), 
            limitPrice=(buyPrice - buyPrice*sl), 
            size=size
        )
