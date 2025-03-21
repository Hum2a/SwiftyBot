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
    select_best_tweet,
    clean_queue_of_duplicates,
    is_duplicate_tweet,
    get_previously_tweeted_texts,
    LAST_API_CHECK,
    API_CHECK_INTERVAL
)

# Rate limiting constants
MIN_API_CALL_INTERVAL = 60  # Minimum seconds between API calls
RATE_LIMIT_BACKOFF = 900    # Seconds to wait after hitting a rate limit (15 minutes)
last_api_call_time = 0      # Track when we last made an API call

def safe_api_call(func, *args, **kwargs):
    """
    Wrapper for API calls to implement rate limiting
    Returns the result of the API call or None if rate limited
    """
    global last_api_call_time
    
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time
    
    # Check if we need to wait
    if time_since_last_call < MIN_API_CALL_INTERVAL:
        wait_time = MIN_API_CALL_INTERVAL - time_since_last_call
        log_activity(f"Rate limiting: waiting {wait_time:.1f} seconds before next API call")
        time.sleep(wait_time)
    
    # Make the API call
    try:
        result = func(*args, **kwargs)
        last_api_call_time = time.time()
        return result
    except tweepy.errors.TooManyRequests:
        log_activity(f"Hit Twitter rate limit! Backing off for {RATE_LIMIT_BACKOFF/60} minutes")
        time.sleep(RATE_LIMIT_BACKOFF)
        return None
    except Exception as e:
        log_activity(f"API call error: {e}")
        return None

class SwiftieBot:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        self.personality_types = list(SYSTEM_PROMPTS.keys())
        self.min_queue_size = 1  # Minimum number of tweets to keep in queue
        self.batch_size = 5      # Number of tweets to generate at once
        self.min_score = 9.0     # Minimum score for a tweet to be queued
        # Load previously tweeted texts on startup
        self.previously_tweeted = get_previously_tweeted_texts()
        log_activity(f"Loaded {len(self.previously_tweeted)} previously tweeted texts")
        # Track rate limit status
        self.rate_limited = False
        self.rate_limit_reset_time = 0

    def refresh_previously_tweeted(self):
        """Refresh the set of previously tweeted texts"""
        self.previously_tweeted = get_previously_tweeted_texts()
        log_activity(f"Refreshed previously tweeted texts: {len(self.previously_tweeted)} entries")

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
        
        # Add to our in-memory set of previously tweeted texts
        self.previously_tweeted.add(tweet_text)
        log_activity("Added to in-memory set of previously tweeted texts")
            
    def clean_queue(self):
        """Clean the queue of any duplicate tweets - using only local checks by default"""
        log_activity("Cleaning queue of duplicate tweets (local checks only)")
        # Make sure we have the latest tweets
        self.refresh_previously_tweeted()
        
        # By default, only use local checks to avoid API rate limits
        # This will still remove duplicates found in Tweeted_tweets.txt
        removed_count = clean_queue_of_duplicates(None)  # Pass None to avoid API check
        
        if removed_count > 0:
            log_activity(f"Removed {removed_count} duplicate tweets from queue")
        return removed_count
            
    def save_all_generated_tweets(self, all_tweets, chosen_tweet=None):
        """Save all generated tweets to file with timestamp and selection status"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open("All_generated_tweets.txt", "a", encoding="utf-8") as f:
            f.write(f"\n===== TWEET GENERATION SESSION: {timestamp} =====\n\n")
            
            for i, tweet in enumerate(all_tweets):
                status = "CHOSEN" if chosen_tweet and tweet["text"] == chosen_tweet["text"] else "NOT CHOSEN"
                
                # Check score threshold for queueing
                if tweet.get("score", 0) >= self.min_score and status != "CHOSEN":
                    # Check if this tweet text has been tweeted before
                    if tweet["text"] in self.previously_tweeted:
                        status = f"{status} & DUPLICATE (NOT QUEUED)"
                    else:
                        status = f"{status} & QUEUED"
                
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

    def check_tweet_for_duplicates(self, tweet_text):
        """
        Check if a tweet is a duplicate using only local records
        Returns True if it's unique, False if it's a duplicate
        """
        # First check against our in-memory set (fastest)
        if tweet_text in self.previously_tweeted:
            log_activity("Tweet is a duplicate (found in memory)")
            return False
            
        # Then check against the file directly (in case memory set is stale)
        latest_tweeted = get_previously_tweeted_texts()
        if tweet_text in latest_tweeted:
            # Update our in-memory set while we're at it
            self.previously_tweeted = latest_tweeted
            log_activity("Tweet is a duplicate (found in file)")
            return False
            
        # If we got here, it's not a duplicate in our local records
        return True

    def replenish_queue_if_needed(self):
        """Check queue size and generate more tweets if needed"""
        # First clean the queue of any duplicates
        self.clean_queue()
        
        # Then check the size
        current_size = queue_size()
        log_activity(f"Current queue size: {current_size}")
        
        if current_size < self.min_queue_size:
            log_activity(f"Queue below minimum size ({self.min_queue_size}), generating new batch")
            
            # Make sure we have the latest set of previously tweeted texts
            self.refresh_previously_tweeted()
            
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
            # Check if we're currently rate limited
            if self.rate_limited:
                current_time = time.time()
                if current_time < self.rate_limit_reset_time:
                    wait_time = self.rate_limit_reset_time - current_time
                    log_activity(f"Still rate limited. Waiting {wait_time/60:.1f} more minutes.")
                    return False
                else:
                    log_activity("Rate limit period has passed. Resuming normal operation.")
                    self.rate_limited = False
            
            # Make sure we have the latest previously tweeted texts
            self.refresh_previously_tweeted()
            
            # Replenish queue if needed (this uses local checks only)
            self.replenish_queue_if_needed()
            
            # Try to get a tweet from the queue first
            tweet_data = get_next_tweet_from_queue(None)  # No API check to avoid rate limits
            source = "queue"
            
            # If queue is empty, generate a new tweet
            if not tweet_data:
                log_activity("Queue empty or all queued tweets are duplicates, generating new tweet")
                
                # Make a fresh batch since we need a tweet right now
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
            
            # Check for duplicates using only local records to avoid rate limits
            if not self.check_tweet_for_duplicates(tweet_text):
                log_activity(f"Tweet is a duplicate, skipping: {tweet_text}")
                return False
            
            log_activity(f"Posting tweet from {source} (personality: {personality}): {tweet_text}")
            
            # Post the tweet using rate-limited API call
            response = safe_api_call(self.client.create_tweet, text=tweet_text)
            
            if response is None:
                # We hit a rate limit or other API error
                log_activity("Failed to post tweet due to API error or rate limit. Will try again later.")
                self.rate_limited = True
                self.rate_limit_reset_time = time.time() + RATE_LIMIT_BACKOFF
                return False
            
            log_activity(f"Tweet posted successfully: {tweet_text}")
            self.save_tweet(tweet_text, personality)
            log_activity("Tweet saved to Tweeted_tweets.txt")
            return True
        except Exception as e:
            log_activity(f"Error posting tweet: {e}")
            if "429" in str(e) or "Too Many Requests" in str(e):
                log_activity("Rate limit detected. Backing off.")
                self.rate_limited = True
                self.rate_limit_reset_time = time.time() + RATE_LIMIT_BACKOFF
            return False

    def run(self):
        """Run the bot continuously"""
        log_activity("Bot started")
        
        # Initial clean and queue check - using only local checks
        log_activity("Cleaning tweet queue and checking size on startup")
        self.clean_queue()  # Local checks only
        self.replenish_queue_if_needed()
        
        while True:
            try:
                if self.post_tweet():
                    interval = self.get_random_interval()
                    log_activity(f"Waiting {interval/60:.1f} minutes until next tweet")
                    log_activity(f"Current queue size: {queue_size()}")
                    time.sleep(interval)
                else:
                    # If we're rate limited, wait longer
                    if self.rate_limited:
                        wait_time = min(RATE_LIMIT_BACKOFF, 15 * 60)  # 15 minutes max
                        log_activity(f"Rate limited. Waiting {wait_time/60:.1f} minutes before retry")
                        time.sleep(wait_time)
                    else:
                        log_activity("Tweet failed, retrying in 5 minutes")
                        time.sleep(300)
            except Exception as e:
                log_activity(f"Unexpected error: {e}")
                time.sleep(300)

if __name__ == "__main__":
    bot = SwiftieBot()
    bot.run() 