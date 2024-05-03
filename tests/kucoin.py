from classes.ExchangeFactory import ExchangeFactory

cex = ExchangeFactory('kucoin')
token_ticker = 'TT'

amount = '5'
tp = '2'
sl = '0.7'

bought_tokens = cex.new_buy_order(token_ticker, amount)
bought_price = float(amount) / float(bought_tokens) 
print(f'Bought_price: {bought_price}')
cex.new_sell_oco_order(token_ticker, bought_tokens, bought_price, float(tp), float(sl))

print('Final profit: OCO order placed, cannot look at profit')