import os
import pytz
import asyncio
import logging
from dotenv import load_dotenv
from datetime import datetime, timezone
from channels_config import channels_config
from telethon.sessions import StringSession
from telethon.sync import TelegramClient, events
from classes.ExchangeFactory import ExchangeFactory
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.Formatter.converter = lambda *_: datetime.now(tz=pytz.timezone("Europe/Rome")).timetuple()
logging.getLogger('telethon').setLevel(level=logging.INFO)
logging.getLogger('asyncio').setLevel(level=logging.ERROR)
logging.getLogger('tzlocal').setLevel(level=logging.ERROR)
logging.getLogger('urllib3').setLevel(level=logging.ERROR)
logging.getLogger('apscheduler').setLevel(level=logging.ERROR)
load_dotenv(override=True)
logging.basicConfig(format='[ %(levelname) 5s - %(asctime)s ] %(name)s: %(message)s', datefmt="%d/%m/%Y %H:%M:%S", level=os.getenv('LOG_LEVEL') or logging.INFO)


def pump(channel, message):
    token_ticker = channel.get_ticker(message)
    
    if token_ticker:
        if channel.exchange is None:
            logging.log(logging.ERROR, f'No exchange found for: {channel.name}')
            return
        
        logging.log(logging.INFO, f'"{channel.name}" -> found ticker: {token_ticker} for Exchange: {channel.exchange}')

        cex = ExchangeFactory(channel.exchange)
        if not cex:
            logging.log(logging.ERROR, f'Exchange "{channel.exchange}" does not exist')
            return
        
        # logging.log(logging.DEBUG, f'"{channel.name}" -> I would have bought {token_ticker} at {channel.exchange}')
        
        try:
            bought_tokens = cex.new_buy_order(token_ticker, os.getenv('AMOUNT'))
            bought_price = float(os.getenv('AMOUNT')) / float(bought_tokens) 
            profit = cex.new_sell_oco_order(token_ticker, bought_tokens, bought_price, float(os.getenv('TP')), float(os.getenv('SL')))
            
            logging.log(logging.INFO, '"{0}" -> ticker: {1}/{2}; PROFIT: {:.2f}x'.format(channel.name, token_ticker, channel.exchange, profit))
        except Exception as e:
            logging.log(logging.ERROR, f'{channel.name}: {token_ticker} {e}')

        channel.exchange = None
        return

    logging.log(logging.DEBUG, f'"{channel.name}" -> no ticker found in message: ' + message.replace('\n', ''))

async def ticker_polling(client, channel):
    sec_among_requests = 2
    read_message_for_sec = 45
    logging.log(logging.DEBUG, f'{channel.name}: ticker polling job started')

    for _ in range(0, int(read_message_for_sec / sec_among_requests)):
        message = (await client.get_messages(channel.name, limit=1))[0]
        time_delta = datetime.now(timezone.utc) - message.date
        if time_delta.total_seconds() < read_message_for_sec:
            pump(channel, message.message)
            return

        await asyncio.sleep(sec_among_requests)
    logging.log(logging.DEBUG, f'{channel.name}: no new message in {read_message_for_sec}sec...')

async def main():
    async with TelegramClient(StringSession(os.getenv('TELEGRAM_SESSION')), int(os.getenv('TELEGRAM_API_ID')), os.getenv('TELEGRAM_API_HASH')) as client:
        @client.on(events.NewMessage(chats=[ channel.name for channel in channels_config ]))
        async def check_cex_message(event):
            channel = next(x for x in channels_config if x.name == event.chat.username)
            ch_exchange = channel.get_cex(event.message.message)

            if ch_exchange:
                logging.log(logging.INFO, f'"{event.chat.username}" -> found exchange: {ch_exchange}')
                channel.exchange = ch_exchange
                return
            
            logging.log(logging.DEBUG, f'"{channel.name}" -> no exchange found in message: ' + event.message.message.replace('\n', ''))
            logging.log(logging.DEBUG, 'Current channel_config -> ' + str([ f'Channel: {x.name}; Cex: {x.exchange}' for x in channels_config ]))

        scheduler = AsyncIOScheduler()
        for x in channels_config:
            scheduler.add_job(ticker_polling, 'cron', [client, x], hour='*/1')

        scheduler.start()

        await client.run_until_disconnected()

        # while True:
        #     await asyncio.sleep(1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
