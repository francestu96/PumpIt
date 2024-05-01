from classes.Channel import Channel

channels_config = [
    Channel('Binance_Pumps_Signals_Crypto', 
            cex_re='Exchange: ([a-zA-Z]+)[.][a-z]{3}',
            ticker_re='^([A-Z]{2,6})$'),

    Channel('Crypto_Binance_Kucoin',
            cex_re='Exchange : ([A-Z]+)',            
            ticker_re='^The coin we are pumping today is : ([A-Z]{2,6})$'),

    Channel('pump_it_0', 
            cex_re='Exchange: ([a-zA-Z]+)[.][a-z]{3}', 
            ticker_re='^([A-Z]{2,6})$'),
]
