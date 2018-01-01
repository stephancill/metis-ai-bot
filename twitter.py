from config import Config
import requests
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

class TwitterListener(StreamListener):
	def __init__(self, callback):
		self.callback = callback

	def on_data(self, data):
		tweet_json = json.loads(data)
		try: 
			if tweet_json["user"]["id_str"] in Config.follow_ids:
				# print(data)
				self.callback(tweet_json["text"])
		except:
			pass
		
class Twitter:
	def __init__(self):
		with open("secrets.json") as f:
			keys = json.load(f) 
			CONSUMER_KEY = keys["TWITTER_CONSUMER_KEY"]
			CONSUMER_SECRET = keys["TWITTER_CONSUMER_SECRET"]
			ACCESS_KEY = keys["TWITTER_ACCESS_KEY"]
			ACCESS_SECRET = keys["TWITTER_ACCESS_SECRET"]
		
		self.auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		self.auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)

		self.listener = None
		self.stream = None
	
	def listen(self, callback):
		print("Listening")
		self.listener = TwitterListener(callback)
		self.stream = Stream(self.auth, self.listener)	
		self.stream.filter(follow=Config.follow_ids, async=True)

if __name__ == "__main__":
	def tweet_callback(tweet_json):
		pass
	twitter = Twitter()
	twitter.listen(tweet_callback)