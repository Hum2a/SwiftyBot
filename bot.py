import tweepy
import time
import random
from datetime import datetime
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    SYSTEM_PROMPTS
)
from tweet_generator import generate_tweet
from utils import log_activity
from tweet_selector import get_optimal_tweet, generate_multiple_tweets, select_best_tweet

class SwiftieBot:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        self.personality_types = list(SYSTEM_PROMPTS.keys())

    def get_random_interval(self):
        """Get a random interval between 13 and 38 minutes in seconds"""
        return random.randint(13 * 60, 38 * 60)

    def get_random_personality(self):
        """Get a random personality type"""
        return random.choice(self.personality_types)

    def save_tweet(self, tweet_text, personality):
        """Save tweet to file with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("Tweeted_tweets.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}] - {personality}\n")
            f.write(tweet_text)
            f.write("\n" + "-"*50 + "\n")
            
    def save_all_generated_tweets(self, all_tweets, chosen_tweet=None):
        """Save all generated tweets to file with timestamp and selection status"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("All_generated_tweets.txt", "a", encoding="utf-8") as f:
            f.write(f"\n===== TWEET GENERATION SESSION: {timestamp} =====\n\n")
            
            for i, tweet in enumerate(all_tweets):
                status = "CHOSEN" if chosen_tweet and tweet["text"] == chosen_tweet["text"] else "NOT CHOSEN"
                f.write(f"[{i+1}] - {tweet['personality']} - {status}\n")
                f.write(tweet["text"])
                f.write("\n" + "-"*30 + "\n")
                
            f.write("\n" + "="*50 + "\n")
        
        log_activity(f"Saved {len(all_tweets)} generated tweets to All_generated_tweets.txt")

    def post_tweet(self):
        """Generate and post a tweet"""
        try:
            # Generate multiple tweets
            all_tweets = generate_multiple_tweets(count=5)
            
            if not all_tweets:
                log_activity("Failed to generate tweets")
                return False
            
            # Select the best tweet
            tweet_data = select_best_tweet(all_tweets)
            
            if not tweet_data:
                log_activity("Failed to select best tweet")
                return False
            
            tweet_text = tweet_data["text"]
            personality = tweet_data["personality"]
            
            # Save all generated tweets, marking the chosen one
            self.save_all_generated_tweets(all_tweets, tweet_data)
            
            log_activity(f"Posting tweet (personality: {personality}): {tweet_text}")
            
            # Post the tweet using your working API method (v2)
            response = self.client.create_tweet(text=tweet_text)
            
            log_activity(f"Tweet posted successfully: {tweet_text}")
            self.save_tweet(tweet_text, personality)
            log_activity("Tweet saved to Tweeted_tweets.txt")
            return True
        except Exception as e:
            log_activity(f"Error posting tweet: {e}")
            return False

    def run(self):
        """Run the bot continuously"""
        log_activity("Bot started")
        while True:
            try:
                if self.post_tweet():
                    interval = self.get_random_interval()
                    log_activity(f"Waiting {interval/60:.1f} minutes until next tweet")
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