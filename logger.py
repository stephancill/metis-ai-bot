from config import Config
import json
import os
import requests

class Logger:
	def log(*msg):
		print(*msg)
		Logger.broadcast(*msg)

	def broadcast(*msg):
		try:
			with open("secrets.json") as f:
				keys = json.load(f) 
				BOT_TOKEN = keys["TELEGRAM_BOT_TOKEN"]
		except:
			BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]

		chat_ids = ["@" + x for x in Config.telegram_log_channels]

		for chat_id in chat_ids:
			endpoint = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={" ".join([str(x) for x in msg])}'
			print(requests.get(endpoint))

if __name__ == "__main__":
	Logger.log("test", (1, 2, 3))