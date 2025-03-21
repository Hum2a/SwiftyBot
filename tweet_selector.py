import random
import json
import os
import re
import time
from tweet_generator import generate_tweet, generate_trending_tweet

# File to store queued tweets
TWEET_QUEUE_FILE = "tweet_queue.json"
# File containing previously tweeted tweets
TWEETED_TWEETS_FILE = "Tweeted_tweets.txt"
# Cache recent tweets from API to reduce calls
RECENT_TWEETS_CACHE = set()
# Last time we checked the Twitter API
LAST_API_CHECK = 0
# Minimum time between API checks (in seconds)
API_CHECK_INTERVAL = 900  # 15 minutes

def load_tweet_queue():
    """Load the tweet queue from file"""
    if not os.path.exists(TWEET_QUEUE_FILE):
        return []
    
    try:
        with open(TWEET_QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tweet queue: {e}")
        return []

def save_tweet_queue(queue):
    """Save the tweet queue to file"""
    try:
        with open(TWEET_QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving tweet queue: {e}")

def get_previously_tweeted_texts():
    """Extract all previously tweeted texts from the Tweeted_tweets.txt file"""
    tweeted_texts = set()
    
    if not os.path.exists(TWEETED_TWEETS_FILE):
        return tweeted_texts
    
    try:
        with open(TWEETED_TWEETS_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Find tweet content between timestamp lines and separator lines
            # Pattern: looking for content between a line with timestamp and a line with dashes
            tweet_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] - .*?\n(.*?)\n-{50}'
            tweets = re.findall(tweet_pattern, content, re.DOTALL)
            
            for tweet in tweets:
                # Clean the tweet text (remove extra whitespace)
                clean_tweet = tweet.strip()
                if clean_tweet:
                    tweeted_texts.add(clean_tweet)
                    
    except Exception as e:
        print(f"Error reading previously tweeted tweets: {e}")
        
    return tweeted_texts

def is_duplicate_tweet(text, api_client=None):
    """
    Check if a tweet is a duplicate by:
    1. Checking local records (Tweeted_tweets.txt)
    2. Optionally checking Twitter API if client is provided BUT only if enough time has passed
    """
    global RECENT_TWEETS_CACHE, LAST_API_CHECK
    
    # Check local records first
    previously_tweeted = get_previously_tweeted_texts()
    if text in previously_tweeted:
        return True
    
    # Check our cached API results
    if text in RECENT_TWEETS_CACHE:
        return True
    
    # If API client is provided AND enough time has passed since last check, refresh from API
    current_time = time.time()
    if api_client and (current_time - LAST_API_CHECK) > API_CHECK_INTERVAL:
        try:
            print(f"Refreshing Twitter API cache (last check was {(current_time - LAST_API_CHECK) / 60:.1f} minutes ago)")
            # Get user ID from authenticated user
            user_data = api_client.get_me()
            user_id = user_data.data.id
            
            # Get recent tweets (up to 50 - reduced from 100 to help with rate limits)
            recent_tweets = api_client.get_users_tweets(
                id=user_id, 
                max_results=50,
                tweet_fields=['text']
            )
            
            # Update our cache
            RECENT_TWEETS_CACHE.clear()
            if recent_tweets.data:
                for tweet in recent_tweets.data:
                    RECENT_TWEETS_CACHE.add(tweet.text)
                    
            # Update our last check time
            LAST_API_CHECK = current_time
            
            # Check if our text is in the refreshed cache
            if text in RECENT_TWEETS_CACHE:
                return True
                
        except Exception as e:
            print(f"Error checking Twitter API for duplicates: {e}")
            # If API check fails, we'll rely on local check only
            pass
    
    return False

def clean_queue_of_duplicates(api_client=None):
    """Remove any duplicate tweets from the queue - using local files only by default"""
    global LAST_API_CHECK, RECENT_TWEETS_CACHE
    
    queue = load_tweet_queue()
    previously_tweeted = get_previously_tweeted_texts()
    
    # Check each tweet in the queue against local records
    original_length = len(queue)
    queue = [tweet for tweet in queue if tweet["text"] not in previously_tweeted]
    
    # Only check against Twitter API if explicitly requested AND we need to refresh
    if api_client and (time.time() - LAST_API_CHECK) > API_CHECK_INTERVAL:
        try:
            # Get user ID from authenticated user
            user_data = api_client.get_me()
            user_id = user_data.data.id
            
            # Get recent tweets (up to 50)
            recent_tweets = api_client.get_users_tweets(
                id=user_id, 
                max_results=50,
                tweet_fields=['text']
            )
            
            # Update our cache
            RECENT_TWEETS_CACHE.clear()
            if recent_tweets.data:
                RECENT_TWEETS_CACHE = {tweet.text for tweet in recent_tweets.data}
                queue = [tweet for tweet in queue if tweet["text"] not in RECENT_TWEETS_CACHE]
                
            # Update our last check time
            LAST_API_CHECK = time.time()
                
        except Exception as e:
            print(f"Error checking Twitter API for duplicates: {e}")
            # If API check fails, we'll rely on local check only
            pass
    # If we don't need to refresh, just use our cached results
    elif len(RECENT_TWEETS_CACHE) > 0:
        queue = [tweet for tweet in queue if tweet["text"] not in RECENT_TWEETS_CACHE]
    
    # Save the cleaned queue
    removed_count = original_length - len(queue)
    if removed_count > 0:
        save_tweet_queue(queue)
        print(f"Removed {removed_count} duplicate tweets from queue")
    
    return removed_count

def generate_multiple_tweets(count=5, include_trending=True):
    """Generate multiple tweets with different personality types and return them all"""
    # All available personality types
    all_personality_types = [
        # Taylor Swift personalities
        "OBSESSED_TEEN", 
        "FEMINIST_SWIFTIE", 
        "CONSPIRACY_SWIFTIE", 
        "CHRONICALLY_ONLINE_FAN",
        "TOXIC_STAN",
        "MIDDLE_AGED_SWIFTIE",
        "DELUSIONAL_SUPERFAN",
        
        # Socio-political personalities
        "CONSPIRACY_THEORIST",
        "TECH_BRO_FUTURIST",
        "PSEUDO_INTELLECTUAL",
        "DOOMSDAY_PREPPER",
        "CORPORATE_SHILL",
        "ARMCHAIR_EXPERT",
        "NOSTALGIC_BOOMER"
    ]
    
    # Filter to only socio-political personalities if desired
    # Uncomment the line below to use only socio-political personalities
    # personality_types = all_personality_types[7:]  # Skip the Taylor Swift personalities
    
    # Or use all personalities
    personality_types = all_personality_types
    
    tweets = []
    
    # Generate tweets with different personalities
    for _ in range(count):
        personality = random.choice(personality_types)
        tweet = generate_tweet(personality)
        if tweet:
            tweets.append({
                "text": tweet,
                "personality": personality
            })
    
    # Optionally include a trending tweet
    if include_trending:
        trending_tweet = generate_trending_tweet()
        if trending_tweet:
            tweets.append({
                "text": trending_tweet,
                "personality": "TRENDING"
            })
    
    return tweets

def score_tweet(tweet):
    """Score a tweet based on various criteria and return the scored tweet"""
    score = 0
    text = tweet["text"]
    
    # Length score - prefer tweets between 100-240 characters
    length = len(text)
    if 100 <= length <= 240:
        score += 10
    elif length < 100:
        score += length / 10  # Shorter tweets get lower scores
    else:
        score += (280 - length) / 4  # Approaching the limit lowers score
    
    # Length score details
    length_score = score
    
    # Hashtag score - PENALIZE tweets with hashtags
    hashtag_count = text.count('#')
    hashtag_score = 0
    if hashtag_count > 0:
        hashtag_score = -(hashtag_count * 10)  # Heavily penalize hashtags
        score += hashtag_score
    
    # Emoji score - some emojis are good, too many are bad
    emoji_count = sum(1 for char in text if ord(char) > 127000)
    emoji_score = 0
    if 1 <= emoji_count <= 4:
        emoji_score = 5
        score += emoji_score
    elif emoji_count > 4:
        emoji_score = -((emoji_count - 4) * 2)
        score += emoji_score
    
    # Capitalization for emphasis
    caps_words = sum(1 for word in text.split() if word.isupper() and len(word) > 1)
    caps_score = 0
    if 1 <= caps_words <= 3:
        caps_score = 5
        score += caps_score
    
    # Irony/humor indicators
    irony_score = 0
    if "..." in text or "…" in text:
        irony_score += 3  # Ellipsis often indicates irony
    if "!" in text and "?" in text:
        irony_score += 3  # Exclamation and question marks together often indicate humor
    score += irony_score
    
    # Add score breakdown to the tweet data
    tweet_with_score = tweet.copy()
    tweet_with_score["score"] = score
    tweet_with_score["score_breakdown"] = {
        "total": score,
        "length": {
            "value": length,
            "score": length_score
        },
        "hashtags": {
            "count": hashtag_count,
            "score": hashtag_score
        },
        "emojis": {
            "count": emoji_count,
            "score": emoji_score
        },
        "caps_words": {
            "count": caps_words,
            "score": caps_score
        },
        "irony_indicators": {
            "score": irony_score
        }
    }
    
    return tweet_with_score

def score_and_queue_tweets(tweets, min_score=9.0):
    """
    Score tweets and add those that meet the threshold to the queue
    Returns all scored tweets and the number of tweets added to queue
    """
    # Load existing queue
    queue = load_tweet_queue()
    
    # Track existing tweet texts to avoid duplicates
    existing_texts = {tweet["text"] for tweet in queue}
    
    # Also check previously tweeted tweets
    previously_tweeted = get_previously_tweeted_texts()
    
    # And check our cache of recent tweets from the API
    global RECENT_TWEETS_CACHE
    
    # Score all tweets
    scored_tweets = [score_tweet(tweet) for tweet in tweets]
    
    # Add qualified tweets to the queue
    added_count = 0
    for tweet in scored_tweets:
        # Check if the tweet meets minimum score and isn't a duplicate
        if (tweet["score"] >= min_score and 
            tweet["text"] not in existing_texts and
            tweet["text"] not in previously_tweeted and
            tweet["text"] not in RECENT_TWEETS_CACHE):
            queue.append(tweet)
            existing_texts.add(tweet["text"])
            added_count += 1
    
    # Save updated queue
    save_tweet_queue(queue)
    
    return scored_tweets, added_count

def get_next_tweet_from_queue(api_client=None):
    """Get the next tweet from the queue and remove it"""
    queue = load_tweet_queue()
    
    if not queue:
        return None
    
    # Clean queue using only local checks to avoid API rate limits
    clean_queue_of_duplicates(None)  # Pass None to avoid API check
    
    # Reload queue after cleaning
    queue = load_tweet_queue()
    if not queue:
        return None
    
    # Get the first tweet - we trust our local checks
    next_tweet = queue.pop(0)
    save_tweet_queue(queue)
    return next_tweet

def queue_size():
    """Return the number of tweets in the queue"""
    queue = load_tweet_queue()
    return len(queue)

def select_best_tweet(tweets):
    """
    Select the best tweet based on scoring criteria
    """
    if not tweets:
        return None
    
    # Score all tweets if they aren't already scored
    scored_tweets = []
    for tweet in tweets:
        if "score" not in tweet:
            scored_tweet = score_tweet(tweet)
            scored_tweets.append((scored_tweet["score"], scored_tweet))
        else:
            scored_tweets.append((tweet["score"], tweet))
    
    # Sort by score and return the highest-scoring tweet
    scored_tweets.sort(reverse=True)
    return scored_tweets[0][1]

def get_optimal_tweet():
    """Generate multiple tweets and select the best one"""
    tweets = generate_multiple_tweets(count=5)
    return select_best_tweet(tweets)

def generate_and_queue_tweets(count=5, min_score=9.0):
    """
    Generate multiple tweets, score them, add qualifying ones to the queue,
    and return the best one for immediate posting
    """
    # Generate tweets
    tweets = generate_multiple_tweets(count=count)
    
    if not tweets:
        return None, 0
    
    # Score and queue tweets - no API check here, just local
    scored_tweets, added_count = score_and_queue_tweets(tweets, min_score)
    
    # Select the best tweet for immediate posting
    best_tweet = select_best_tweet(scored_tweets)
    
    return best_tweet, added_count

# Initialize the API check time on module load
LAST_API_CHECK = time.time() - API_CHECK_INTERVAL - 1  # Set to ensure first check works 