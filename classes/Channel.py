import re

class Channel:
    def __init__(self, name, cex_re, ticker_re, exchange=None):
        self.name = name
        self.cex_re = cex_re
        self.ticker_re = ticker_re
        self.exchange = exchange

    def get_cex(self, message):
        match = re.findall(self.cex_re, message) 

        if len(match) > 0:
            if isinstance(match[0], str):
                return match[0].lower()
            
            elif type(match[0]) is tuple:
                for v in match[0]:
                    if v: return v.lower() 
            
            raise Exception("Unable to parse exchange message corractly. Match found: " + str(match))
        
        return None
    
    def get_ticker(self, message):
        match = re.findall(self.ticker_re, message)

        if len(match) > 0:
            if isinstance(match[0], str):
                return match[0]
            
            elif type(match[0]) is tuple:
                for v in match[0]:
                    if v: return v 
            
            raise Exception("Unable to parse ticker message corractly. Match found: " + str(match))
        
        return None