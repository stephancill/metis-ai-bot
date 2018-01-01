from main import Main
from twitter import Twitter
import json

"""
DISCLAIMER - BITTREX TESTS WILL MAKE REAL TRANSACTIONS
"""

def test_extract_symbol_price():
	with open("sample-tweets.json") as f:
		sample_tweets = json.load(f)
	
	main = Main()
	
	# Price
	symbol, price = main.extract_symbol_price(sample_tweets["price"]["text"])
	assert (symbol, price) == ("CANN", 0.000025)

	# Update
	symbol, price = main.extract_symbol_price(sample_tweets["update"]["text"])
	assert (symbol, price) == (None, None)

def test_tweet_handler():
	with open("sample-tweets.json") as f:
		sample_tweets = json.load(f)
	
	main = Main()

	main.handle_tweet(sample_tweets["price"]["text"])

if __name__ == "__main__":
	# test_tweet_handler()