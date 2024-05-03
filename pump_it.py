import os
import logging
from dotenv import load_dotenv
from channels_config import channels_config
from telethon.sessions import StringSession
from telethon.sync import TelegramClient, events
from classes.ExchangeFactory import ExchangeFactory

logging.getLogger('telethon').setLevel(level=logging.INFO)
load_dotenv(override=True)
logging.basicConfig(format='[ %(levelname) 5s - %(asctime)s ] %(name)s: %(message)s', datefmt="%d/%m/%Y %H:%M:%S", level=os.getenv('LOG_LEVEL') or logging.INFO)

with TelegramClient(StringSession(os.getenv('TELEGRAM_SESSION')), int(os.getenv('TELEGRAM_API_ID')), os.getenv('TELEGRAM_API_HASH')) as client:
    @client.on(events.NewMessage(chats=[ channel.name for channel in channels_config ]))
    async def handler(event):
        channel = next(x for x in channels_config if x.name == event.chat.username)
        ch_exchange = channel.get_cex(event.message.message)
        token_ticker = channel.get_ticker(event.message.message)

        if ch_exchange:
            logging.log(logging.DEBUG, f'"{event.chat.username}" -> exchange found in message: {ch_exchange}')
            channel.exchange = ch_exchange

        elif token_ticker:
            if channel.exchange is None:
                logging.log(logging.ERROR, f'No exchange found for: {event.chat.username}')
                return
            
            logging.log(logging.INFO, f'"{event.chat.username}" -> found ticker: {token_ticker} for Exchange: {channel.exchange}')

            cex = ExchangeFactory(channel.exchange)
            if not cex:
                logging.log(logging.ERROR, f'Exchange "{channel.exchange}" does not exist')
                return
            
            bought_tokens = cex.new_buy_order(token_ticker, os.getenv('AMOUNT'))
            bought_price = float(os.getenv('AMOUNT')) / float(bought_tokens) 
            profit = cex.new_sell_oco_order(token_ticker, bought_tokens, bought_price, float(os.getenv('TP')), float(os.getenv('SL')))
            
            if profit:
                logging.log(logging.INFO, '"{0}" -> ticker: {1}/{2}; PROFIT: {:.2f}x'.format(event.chat.username, token_ticker, channel.exchange, profit))
            else:
                logging.log(logging.INFO, '"{0}" -> ticker: {1}/{2}; Final profit: OCO order placed, cannot look at profit'.format(event.chat.username, channel.exchange, token_ticker))

            channel.exchange = None

        else:
            logging.log(logging.DEBUG, f'"{event.chat.username}" -> no info found in message: ' + event.message.message.replace('\n', ''))

        logging.log(logging.DEBUG, 'Current channel_config -> ' + {[ f'Channel: {x.name}; Cex: {x.exchange}' for x in channels_config ]})

    client.run_until_disconnected()