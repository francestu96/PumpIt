import re

class Channel:
    def __init__(self, name, cex_re, ticker_re, exchange=None):
        self.name = name
        self.cex_re = cex_re
        self.ticker_re = ticker_re
        self.exchange = exchange

    def get_cex(self, message):
        cex_re = re.search(self.cex_re, message) 
        if cex_re:
           return cex_re.group(1).lower()
        
        return None
    
    def get_ticker(self, message):
        ticker_re = re.search(self.ticker_re, message) 
        if ticker_re:
           return ticker_re.group(1)
        
        return None