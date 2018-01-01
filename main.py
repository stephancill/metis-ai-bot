#!/usr/bin/env python
from config import Config
from exchanges import Bittrex
import json
import logging
from textblob import TextBlob
import time
import traceback
from twitter import Twitter

class Main:
	def __init__(self):
		self.twitter = Twitter()
		self.bittrex = Bittrex()
		self.symbols = self.bittrex.get_markets()

	def extract_symbol_price(self, text):
		try:
			if "Price:" in text and "$" in text:
				symbol = TextBlob(text.split("$")[1]).words[0]
				price = float([x[0] for x in TextBlob(text.split("Price: ")[1]).tags if x[1] == "CD"][0])
				return symbol, price
			else:
				return None, None
		except Exception as e:
			print(e)

	def handle_tweet(self, text):
		symbol, price = self.extract_symbol_price(text)
		if symbol and price:
			print(f'New signal: {symbol, "{:.8f}".format(price)}')
			if symbol in self.symbols:
				self.buy_and_sell(symbol)
		
	def buy_and_sell(self, symbol):
		try:
			# Initiate market buy
			pair = f'BTC-{symbol}'
			amount = round(self.bittrex.get_portfolio_value() * Config.btc_spend_multiplier, 8)
			print(f'Spending {"{:.8f}".format(amount)} BTC')
			uuid, buy_price = self.bittrex.market_buy(pair, amount)
			# Wait for the order to close
			if self.bittrex.wait_for_order(uuid):
				print("Buy order filled")
				# Create sell order
				rate = round(buy_price * Config.sell_multiplier, 8)
				self.bittrex.limit_sell_by_order(uuid, rate)
				print("Sell order placed successfully")
			else:
				# Cancel order if timed out
				print("Market buy took too long... canceling")
				self.bittrex.cancel_order(uuid)
		except Exception as e:
			traceback.print_tb(e.__traceback__)

	def run(self):
		self.twitter.listen(self.handle_tweet)


if __name__ == "__main__":
	Main().run()

	"""
	TODO
	[x] Listen for tweets from @metis_ai
	[x] Extract symbol and price
	[x] Buy symbol at market price and sell for profit specified in config
	[ ] Test market buy
	"""
	
	
