import sys
from classes.ExchangeFactory import ExchangeFactory

cex = ExchangeFactory('mexc')
token_ticker = sys.argv[1].upper()

amount = '10'
tp = '2'
sl = '0.75'

bought_tokens = cex.new_buy_order(token_ticker, amount)
bought_price = float(amount) / float(bought_tokens) 
print(f'Bought_price: {bought_price}')
profit = cex.new_sell_tp_sl_order(token_ticker, bought_tokens, bought_price, float(tp), float(sl))

print('Final profit: {:.2f}x'.format(profit))