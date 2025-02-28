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
from tweet_selector import (
    generate_and_queue_tweets, 
    get_next_tweet_from_queue,
    queue_size,
    generate_multiple_tweets,
    score_and_queue_tweets,
    select_best_tweet
)

class SwiftieBot:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        self.personality_types = list(SYSTEM_PROMPTS.keys())
        self.min_queue_size = 3  # Minimum number of tweets to keep in queue
        self.batch_size = 5      # Number of tweets to generate at once
        self.min_score = 12.0    # Minimum score for a tweet to be queued

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
                queued = "QUEUED" if tweet.get("score", 0) >= self.min_score and status != "CHOSEN" else ""
                if queued:
                    status = f"{status} & {queued}"
                
                # Check if score data is available
                score_info = ""
                if "score" in tweet:
                    score_info = f" - SCORE: {tweet['score']:.2f}"
                    
                    # Add score breakdown if available
                    if "score_breakdown" in tweet:
                        bd = tweet["score_breakdown"]
                        score_info += f"\n  Length: {bd['length']['value']} chars (score: {bd['length']['score']:.2f})"
                        score_info += f"\n  Hashtags: {bd['hashtags']['count']} (score: {bd['hashtags']['score']})"
                        score_info += f"\n  Emojis: {bd['emojis']['count']} (score: {bd['emojis']['score']})"
                        score_info += f"\n  Caps Words: {bd['caps_words']['count']} (score: {bd['caps_words']['score']})"
                        score_info += f"\n  Irony Indicators: score {bd['irony_indicators']['score']}"
                
                f.write(f"[{i+1}] - {tweet['personality']} - {status}{score_info}\n")
                f.write(tweet["text"])
                f.write("\n" + "-"*30 + "\n")
                
            # If we have the chosen tweet with score data, display why it was chosen
            if chosen_tweet and "score" in chosen_tweet:
                f.write("\nCHOSEN TWEET ANALYSIS:\n")
                f.write(f"Personality: {chosen_tweet['personality']}\n")
                f.write(f"Total Score: {chosen_tweet['score']:.2f}\n")
                f.write(f"Character Count: {len(chosen_tweet['text'])}\n")
                
                if "score_breakdown" in chosen_tweet:
                    bd = chosen_tweet["score_breakdown"]
                    f.write(f"Hashtags: {bd['hashtags']['count']}\n")
                    f.write(f"Emojis: {bd['emojis']['count']}\n")
                    f.write(f"CAPS Words: {bd['caps_words']['count']}\n")
                    
            f.write("\n" + "="*50 + "\n")
        
        log_activity(f"Saved {len(all_tweets)} generated tweets to All_generated_tweets.txt")

    def replenish_queue_if_needed(self):
        """Check queue size and generate more tweets if needed"""
        current_size = queue_size()
        log_activity(f"Current queue size: {current_size}")
        
        if current_size < self.min_queue_size:
            log_activity(f"Queue below minimum size ({self.min_queue_size}), generating new batch")
            
            # Generate a batch of tweets
            tweets = generate_multiple_tweets(count=self.batch_size)
            
            if tweets:
                # Score and queue tweets
                scored_tweets, added_count = score_and_queue_tweets(tweets, self.min_score)
                
                # Log the results
                log_activity(f"Generated {len(scored_tweets)} tweets, added {added_count} to queue")
                
                # Save all generated tweets for analysis
                self.save_all_generated_tweets(scored_tweets)
                
                return True
        
        return False

    def post_tweet(self):
        """Get a tweet from the queue or generate a new one, then post it"""
        try:
            # Replenish queue if needed
            self.replenish_queue_if_needed()
            
            # Try to get a tweet from the queue first
            tweet_data = get_next_tweet_from_queue()
            source = "queue"
            
            # If queue is empty, generate a new tweet
            if not tweet_data:
                log_activity("Queue empty, generating new tweet")
                
                # Generate, score, and queue tweets, then get the best one for posting
                tweet_data, added_count = generate_and_queue_tweets(
                    count=self.batch_size, 
                    min_score=self.min_score
                )
                
                source = "new batch"
                log_activity(f"Added {added_count} tweets to queue")
                
            if not tweet_data:
                log_activity("Failed to get a tweet to post")
                return False
            
            tweet_text = tweet_data["text"]
            personality = tweet_data["personality"]
            
            log_activity(f"Posting tweet from {source} (personality: {personality}): {tweet_text}")
            
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
        
        # Initial queue check and replenishment
        log_activity("Checking tweet queue on startup")
        self.replenish_queue_if_needed()
        
        while True:
            try:
                if self.post_tweet():
                    interval = self.get_random_interval()
                    log_activity(f"Waiting {interval/60:.1f} minutes until next tweet")
                    log_activity(f"Current queue size: {queue_size()}")
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