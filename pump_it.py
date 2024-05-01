import os
import logging
from dotenv import load_dotenv
from channels_config import channels_config
from telethon.sessions import StringSession
from telethon.sync import TelegramClient, events
from classes.ExchangeFactory import ExchangeFactory

logging.basicConfig(format='[%(levelname) 5s-%(asctime)s] %(name)s: %(message)s', datefmt="%d/%m/%Y %H:%M:%S", level=os.getenv('LOG_LEVEL') or logging.INFO)
logging.getLogger('telethon').setLevel(level=logging.INFO)
load_dotenv(override=True)

with TelegramClient(StringSession(os.getenv('TELEGRAM_SESSION')), int(os.getenv('TELEGRAM_API_ID')), os.getenv('TELEGRAM_API_HASH')) as client:
    @client.on(events.NewMessage(chats=[ channel.name for channel in channels_config ]))
    async def handler(event):
        logging.log(logging.DEBUG, 'New message in chat "' + event.chat.username + '"')
        channel = next(x for x in channels_config if x.name == event.chat.username)
        ch_exchange = channel.get_cex(event.message.message)
        token_ticker = channel.get_ticker(event.message.message)

        if ch_exchange:
            logging.log(logging.DEBUG, '\n' + event.chat.username + ': exchange found in message: ' + ch_exchange)
            channel.exchange = ch_exchange

        elif token_ticker:
            if channel.exchange is None:
                logging.log(logging.ERROR, '\nNo Exchange found for: ' + event.chat.username)
                return
            
            logging.log(logging.INFO, '\n' + event.chat.username + ': found ticker: ' + token_ticker + ' for Exchange: ' + channel.exchange)

            cex = ExchangeFactory(channel.exchange)
            return
            # price = cex.check_price(token_ticker)
            # buy = cex.buy_order('BUY', 10)
            # # TODO: buy with API

        else:
            logging.log(logging.DEBUG, '\n' + event.chat.username + ': no info found in message:\n' + event.message.message)

    client.run_until_disconnected()