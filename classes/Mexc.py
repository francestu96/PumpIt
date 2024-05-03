import os
import time
from mexc_api.spot import Spot
from classes.Exchange import Exchange
from mexc_api.common.enums import OrderType, Side

class Mexc(Exchange):
    def __init__(self):
        self.oco_timeout = 120
        self.client = Spot(os.getenv('MEXC_API_KEY'), os.getenv('MEXC_API_SECRET'))

    def __get_price(self, token_ticker):
        return float(self.client.market.ticker_price(token_ticker + 'USDT')[0]['price'])

    def new_buy_order(self, token_ticker, size):
        order = self.client.account.new_order(token_ticker + 'USDT',  Side.BUY, OrderType.MARKET, quote_order_quantity=size)
        return order['origQty']
    
    def new_sell_oco_order(self, token_ticker, size, buy_price, tp, sl):
        for i in range(0, self.oco_timeout):
            token_price = self.__get_price(token_ticker)
            print(f'Bought token price: {buy_price}; Current token price: {token_price}')
            if (token_price < buy_price - buy_price*sl) or (token_price > buy_price + buy_price*tp) or (i == self.oco_timeout-1):
                sold_price = self.client.account.new_order(token_ticker + 'USDT', Side.SELL, OrderType.MARKET, quantity=size)['price']
                return float(sold_price) / buy_price
            time.sleep(0.75)