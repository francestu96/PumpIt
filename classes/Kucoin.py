import os
from kucoin.client import Trade
from classes.Exchange import Exchange

class Kucoin(Exchange):
    def __init__(self):
        self.bought_tokens = 0
        self.client = Trade(os.getenv('KUCOIN_API_KEY'), os.getenv('KUCOIN_API_SECRET'), os.getenv('KUCOIN_API_PASSPHRASE'))

    def new_buy_order(self, token_ticker, size):
        order_creation = self.client.create_market_order(token_ticker + '-USDT', 'buy', funds=size)
        order = self.client.get_order_details(order_creation['orderId'])
        return order['dealSize']
    
    def new_sell_oco_order(self, token_ticker, size, buy_price, tp, sl):
        self.client.create_oco_order(
            token_ticker + '-USDT',
            'sell',
            price='{:.6f}'.format(buy_price*tp),
            stopPrice='{:.6f}'.format(buy_price*sl),
            limitPrice='{:.6f}'.format(buy_price*sl),
            size=size
        )
        return None
