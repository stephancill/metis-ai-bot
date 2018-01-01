import json
import requests

class Logger:
	def log(*msg):
		print(*msg)
		Logger.broadcast(*msg)

	def broadcast(*msg):
		with open("secrets.json") as f:
			keys = json.load(f) 
			BOT_TOKEN = keys["TELEGRAM_BOT_TOKEN"]

		chat_ids = ["@tradingbotlogs"]

		for chat_id in chat_ids:
			endpoint = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={chat_id}&text={str(*msg)}'
			print(requests.get(endpoint))

if __name__ == "__main__":
	Logger.log("test")