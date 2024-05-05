import os
import json
import requests
from kucoin.client import Trade
from classes.Exchange import Exchange
from websocket import create_connection

class Kucoin(Exchange):
    def __init__(self):
        self.bought_tokens = 0
        self.client = Trade(os.getenv('KUCOIN_API_KEY'), os.getenv('KUCOIN_API_SECRET'), os.getenv('KUCOIN_API_PASSPHRASE'))
        
        req = requests.post('https://api.kucoin.com/api/v1/bullet-public')
        data = req.json()['data']
        self.ws = create_connection(f"{data['instanceServers'][0]['endpoint']}?token={data['token']}")
        self.ws.recv()

    def new_buy_order(self, token_ticker, size):
        order_creation = self.client.create_market_order(token_ticker + '-USDT', 'buy', funds=size)
        order = self.client.get_order_details(order_creation['orderId'])
        return order['dealSize']
    
    def new_sell_tp_sl_order(self, token_ticker, size, buy_price, tp, sl):
        ws_params = {
            'type': 'subscribe',
            'topic': f'/market/ticker:{token_ticker}-USDT',
            'privateChannel': False,
            'response': True
        }
        self.ws.send(json.dumps(ws_params))
        self.ws.recv()
        
        while True:
            token_price = float(json.loads(self.ws.recv())['data']['bestBid'])
            if (token_price < buy_price - buy_price*sl) or (token_price > buy_price + buy_price*tp):
                order_creation = self.client.create_market_order(token_ticker + '-USDT', 'sell', size=size)
                order = self.client.get_order_details(order_creation['orderId'])
                self.ws.close()
                return order['dealSize'] / buy_price
