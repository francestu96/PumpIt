import os
import json
import time
import requests
from kucoin.client import Trade
from classes.Exchange import Exchange
from websocket import create_connection

class Kucoin(Exchange):
    def __init__(self):
        self.client = Trade(os.getenv('KUCOIN_API_KEY'), os.getenv('KUCOIN_API_SECRET'), os.getenv('KUCOIN_API_PASSPHRASE'))

    def new_buy_order(self, token_ticker, size):
        order_creation = self.client.create_market_order(token_ticker + '-USDT', 'buy', funds=size)
        order = self.client.get_order_details(order_creation['orderId'])
        return order['dealSize']
    
    def new_sell_tp_sl_order(self, token_ticker, size, buy_price, tp, sl):
        req = requests.post('https://api.kucoin.com/api/v1/bullet-public')
        data = req.json()['data']
        
        ping_interval = data['instanceServers'][0]['pingInterval']

        ws = create_connection(f"{data['instanceServers'][0]['endpoint']}?token={data['token']}")
        ping_time = time.time()
        ws.recv()

        ws_params = {
            'type': 'subscribe',
            'topic': f'/market/ticker:{token_ticker}-USDT',
            'privateChannel': False,
            'response': True
        }
        ws.send(json.dumps(ws_params))
        ws.recv()
        
        while True:
            recv = json.loads(ws.recv())

            if time.time() - ping_time > int(ping_interval) / 1000:
                ws.send(json.dumps({'type': 'ping'}))
                ping_time = time.time()

            token_price = float(recv.get('data', {}).get('bestBid', 0))
            if token_price and ((token_price < buy_price*sl) or (token_price > buy_price*tp)):
                order_creation = self.client.create_market_order(token_ticker + '-USDT', 'sell', size=size)
                order = self.client.get_order_details(order_creation['orderId'])
                ws.close()
                return float(order['dealFunds']) / float(order['dealSize']) / buy_price
            
