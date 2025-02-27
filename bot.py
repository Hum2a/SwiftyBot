import tweepy
import time
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)
from tweet_generator import generate_tweet
from utils import get_random_interval, log_activity

class SwiftieBot:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

    def post_tweet(self):
        """Generate and post a tweet"""
        tweet_text = generate_tweet()
        if tweet_text:
            try:
                self.client.create_tweet(text=tweet_text)
                log_activity(f"Tweet posted successfully: {tweet_text}")
                return True
            except Exception as e:
                log_activity(f"Error posting tweet: {e}")
                return False
        return False

    def run(self):
        """Run the bot continuously"""
        log_activity("Bot started")
        while True:
            try:
                if self.post_tweet():
                    interval = get_random_interval()
                    log_activity(f"Waiting {interval/3600:.2f} hours until next tweet")
                    time.sleep(interval)
                else:
                    log_activity("Tweet failed, retrying in 5 minutes")
                    time.sleep(300)
            except Exception as e:
                log_activity(f"Unexpected error: {e}")
                time.sleep(300)

if __name__ == "__main__":
    bot = SwiftieBot()
    bot.run() 