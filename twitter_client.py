
import tweepy
from keys import bearer_token

client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
