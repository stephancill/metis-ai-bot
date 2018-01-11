#!/usr/bin/env python
from config import Config
from exchanges import Bittrex
import json
from logger import Logger
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
			if "Price:" in text and "$" in text and "best price:" not in text.lower() and "now: " not in text.lower():
				symbol = TextBlob(text.split("$")[1]).words[0]
				# price = float([x[0] for x in TextBlob(text.split("Price: ")[1]).tags if x[1] == "CD"][0])
				return symbol
			else:
				return None
		except Exception as e:
			Logger.log(e)

	def handle_tweet(self, text):
		symbol = self.extract_symbol_price(text)
		if symbol:
			Logger.log(f'New signal: {symbol}')
			if symbol in self.symbols:
				self.buy_and_sell(symbol)
		
	def buy_and_sell(self, symbol):
		try:
			# Initiate market buy
			pair = f'BTC-{symbol}'
			amount = Config.btc_spend
			Logger.log(f'Spending {"{:.8f}".format(amount)} BTC')
			uuid, buy_price = self.bittrex.market_buy(pair, amount)
			# Wait for the order to close
			if self.bittrex.wait_for_order(uuid):
				Logger.log("Buy order filled")
				# Create sell order
				rate = round(buy_price * Config.sell_multiplier, 8)
				self.bittrex.limit_sell_by_order(uuid, rate)
				Logger.log("Sell order placed successfully")
			else:
				# Cancel order if timed out
				Logger.log("Market buy took too long... canceling")
				self.bittrex.cancel_order(uuid)
		except Exception as e:
			Logger.log(e)
			traceback.print_tb(e.__traceback__)

	def run(self):
		self.twitter.listen(self.handle_tweet)
		Logger.log("Bot running...")


if __name__ == "__main__":
	Main().run()

	"""
	TODO
	[x] Listen for tweets from @metis_ai
	[x] Extract symbol and price
	[x] Buy symbol at market price and sell for profit specified in config
	[ ] Test market buy
	"""
	
	
