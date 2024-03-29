#!/usr/bin/env python
from bittrex.bittrex import Bittrex as BittrexUtils
from config import Config
import json
from logger import Logger
import os
import requests
import time

class Bittrex:
	def __init__(self):
		try:
			with open("secrets.json") as f:
				keys = json.load(f)
				BITTREX_KEY = keys["BITTREX_KEY"]
				BITTREX_SECRET = keys["BITTREX_SECRET"]
		except:
			BITTREX_KEY = os.environ["BITTREX_KEY"]
			BITTREX_SECRET = os.environ["BITTREX_SECRET"]
		self.bittrex = BittrexUtils(BITTREX_KEY, BITTREX_SECRET)
		self.symbols = None
		self.market_summaries = None

	def get_portfolio_value(self):
		# Markets
		response = self.bittrex.get_market_summaries()
		if response["success"]:
			markets = response["result"]
		# Balances
		response = self.bittrex.get_balances()
		if response["success"]:
			balances = response["result"]
		
		total = 0
		balance_symbols = [x["Currency"] for x in balances]
		
		symbol_market = {}
		symbol_market["USDT"] = [x for x in markets if x["MarketName"] == "USDT-BTC"][0]
		for market in markets:
			if "BTC-" in market["MarketName"]:
				symbol = market["MarketName"].split("-")[1]
				if symbol in balance_symbols:
					symbol_market[symbol] = market

		for balance in balances:
			symbol = balance["Currency"]
			if symbol not in symbol_market:
				continue
			
			if symbol == "BTC":
				total += balance["Balance"]
			elif symbol == "USDT":
				total += balance["Balance"] / symbol_market[symbol]["Bid"]
			else:
				total += symbol_market[symbol]["Bid"] * balance["Balance"]

		return total

	def get_available_balance(self, symbol):
		response = self.bittrex.get_balance(symbol)
		if response["success"]:
			return response["result"]["Available"]
		else:
			return 0

	def market_buy(self, pair, total_price):
		"""Buy a a specified value in the base currency's worth at the current asking price +2%
		pair: market pair
		total_price: btc to spend
		Return order uuid, rate"""
		# Get asking price multiplied by Config.buy_multiplier
		ask = self.bittrex.get_marketsummary(pair)["result"][0]["Ask"]
		rate = round(ask * Config.buy_multiplier, 8)
		quantity = round(total_price / rate - 5 * 10**-9, 8) # Round down
		Logger.log("Buy order", (pair, quantity, "{:.8f}".format(rate)))
		# Create order 
		response = self.bittrex.buy_limit(pair, quantity, rate)
		if response["success"]:
			return response["result"]["uuid"], rate
		else:
			raise Exception(f'Bittrex - market_buy: {response["message"]}')

	def limit_sell_by_order(self, uuid, rate, multiplier=1):
		"""Create a sell order for the total quantity of a filled buy order
		uuid: uuid of order
		rate: rate to place sell order
		multiplier: multiplier for quantity to sell
		Return order uuid"""
		order = self.bittrex.get_order(uuid)["result"]
		pair = order["Exchange"]
		quantity = order["Quantity"]*multiplier
		Logger.log("Sell order", (pair, quantity, "{:.8f}".format(rate)))
		# Create order
		response = self.bittrex.sell_limit(pair, quantity, rate)
		if response["success"]:
			return response["result"]["uuid"]
		else:
			raise Exception(f'Bittrex - limit_sell_by_order: {response["message"]}')

	def wait_for_order(self, uuid, max_retries=10):
		"""Wait for order to complete with timeout
		Return is_close: bool"""
		order = self.bittrex.get_order(uuid)["result"]
		is_closed = not order["IsOpen"]
		retries = 0
		while not is_closed and retries < max_retries:
			# Wait 1 second
			time.sleep(1)
			# Check again
			order = self.bittrex.get_order(uuid)["result"]
			is_closed = not order["IsOpen"]
			# Increment retries
			retries += 1
			print(f'Waiting for buy to close {retries}')
		
		return is_closed

	def cancel_order(self, uuid):
		"""Cancel order by uuid"""
		return self.bittrex.cancel(uuid)["success"]

	def get_order_history(self, pair=None):
		"""Return closed orders"""
		result = self.bittrex.get_order_history(pair)
		if result["success"]:
			return result["result"]
		else:
			raise Exception(f'Bittrex - get_order_history: {result["message"]}')
	
	def get_open_orders(self, pair=None):
		"""Return open orders"""
		result = self.bittrex.get_open_orders(pair)
		if result["success"]:
			return result["result"]
		else:
			raise Exception(f'Bittrex - get_open_orders: {result["message"]}')

	def get_markets(self):
		"""Get symbols of all trading markets"""
		symbols = []
		endpoint = "https://bittrex.com/api/v1.1/public/getmarkets"
		try:
			markets = requests.get(endpoint).json()["result"]
			for market in markets:
				symbol = market["MarketCurrency"]
				symbols.append(symbol)
		except Exception as e:
			raise Exception(f'Bittrex - get_markets: Failed to get markets from {endpoint} ({e})')
		
		self.symbols = symbols
		return symbols

if __name__ == "__main__":
	bittrex = Bittrex()
	print(bittrex.get_available_balance("BTC"))
