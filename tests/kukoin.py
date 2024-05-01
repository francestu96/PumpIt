from classes.ExchangeFactory import ExchangeFactory

cex = ExchangeFactory('kucoin')
token_ticker = 'TT'

buy_order = cex.new_buy_order(token_ticker, "5")
print(buy_order)