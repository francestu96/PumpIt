from classes.Exchange import Exchange
from classes.Kucoin import Kucoin
from classes.Mexc import Mexc

class ExchangeFactory:
    def __new__(cls, cex_name) -> Exchange | None:
        match cex_name:
            case "kucoin":
                return Kucoin()
            case "mexc":
                return Mexc()
            case _:
                return None
