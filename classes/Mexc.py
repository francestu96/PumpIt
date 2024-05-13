import os
import json
import time
from mexc_api.spot import Spot
from classes.Exchange import Exchange
from websocket import create_connection
from mexc_api.common.enums import Interval
from mexc_api.common.enums import OrderType, Side

class Mexc(Exchange):
    def __init__(self):
        self.client = Spot(os.getenv('MEXC_API_KEY'), os.getenv('MEXC_API_SECRET'))

    def new_buy_order(self, token_ticker, size):
        prev_kline = self.client.market.klines(token_ticker + 'USDT', Interval.ONE_MIN, limit=2)[0]
        if(float(prev_kline[4]) / float(prev_kline[1]) > 2):
            raise Exception("SCAM")

        order = self.client.account.new_order(token_ticker + 'USDT',  Side.BUY, OrderType.MARKET, quote_order_quantity=size)
        return order['origQty']
    
    def new_sell_tp_sl_order(self, token_ticker, size, buy_price, tp, sl):
        ws = create_connection("wss://wbs.mexc.com/ws")
        ping_interval = 30
        ping_time = time.time()

        ws_params = { 
            'method': 'SUBSCRIPTION', 
            'params': [ f'spot@public.bookTicker.v3.api@{token_ticker}USDT' ] 
        }
        ws.send(json.dumps(ws_params))
        ws.recv()

        while True:
            recv = json.loads(ws.recv())

            if time.time() - ping_time > ping_interval:
                ws.send(json.dumps({'method': 'PING'}))
                ping_time = time.time()

            token_price = float(recv.get('d', {}).get('b', 0))
            if token_price and ((token_price < buy_price*sl) or (token_price > buy_price*tp)):
                order = self.client.account.new_order(token_ticker + 'USDT', Side.SELL, OrderType.MARKET, quantity=size)['price']
                sold_price = order['price']
                ws.close()
                return float(sold_price) / buy_price
            