import os
import json
from mexc_api.spot import Spot
from classes.Exchange import Exchange
from websocket import create_connection
from mexc_api.common.enums import OrderType, Side

class Mexc(Exchange):
    def __init__(self):
        self.oco_timeout = 60
        self.client = Spot(os.getenv('MEXC_API_KEY'), os.getenv('MEXC_API_SECRET'))
        self.ws = create_connection("wss://wbs.mexc.com/ws")

    def new_buy_order(self, token_ticker, size):
        order = self.client.account.new_order(token_ticker + 'USDT',  Side.BUY, OrderType.MARKET, quote_order_quantity=size)
        return order['origQty']
    
    def new_sell_tp_sl_order(self, token_ticker, size, buy_price, tp, sl):
        ws_params = { 
            'method': 'SUBSCRIPTION', 
            'params': [ f'spot@public.bookTicker.v3.api@{token_ticker}USDT' ] 
        }
        self.ws.send(json.dumps(ws_params))
        self.ws.recv()

        while True:
            token_price = float(json.loads(self.ws.recv())['d']['b'])
            if (token_price < buy_price - buy_price*sl) or (token_price > buy_price + buy_price*tp):
                sold_price = self.client.account.new_order(token_ticker + 'USDT', Side.SELL, OrderType.MARKET, quantity=size)['price']
                self.ws.close()
                return float(sold_price) / buy_price
            