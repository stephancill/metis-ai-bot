import os

class Config:
	follow_ids = ["914663684928139264"] # @metis_ai

	# Spend a fraction of BTC balance per signal (default 10%)
	try:
		btc_spend_multiplier = float(os.environ["btc_spend_multiplier"])
	except:
		btc_spend_multiplier = 0.1
	
	# Price to sell at 
	# buy * sell_multiplier = sell price (default 1.1)
	try:
		sell_multiplier = float(os.environ["sell_multiplier"])
	except:
		sell_multiplier = 1.1

	# Buy price multiplier - price ahead of pump (default 1.02)
	try:
		buy_multiplier = float(os.environ["buy_multiplier"])
	except:
		buy_multiplier = 1.02

