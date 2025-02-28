import random
import json
import os
from tweet_generator import generate_tweet, generate_trending_tweet

# File to store queued tweets
TWEET_QUEUE_FILE = "tweet_queue.json"

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

def generate_multiple_tweets(count=5, include_trending=True):
    """Generate multiple tweets with different personality types and return them all"""
    personality_types = [
        "OBSESSED_TEEN", 
        "FEMINIST_SWIFTIE", 
        "CONSPIRACY_SWIFTIE", 
        "CHRONICALLY_ONLINE_FAN",
        "TOXIC_STAN",
        "MIDDLE_AGED_SWIFTIE",
        "DELUSIONAL_SUPERFAN"
    ]
    
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

def score_and_queue_tweets(tweets, min_score=12.0):
    """
    Score tweets and add those that meet the threshold to the queue
    Returns all scored tweets and the number of tweets added to queue
    """
    # Load existing queue
    queue = load_tweet_queue()
    
    # Track existing tweet texts to avoid duplicates
    existing_texts = {tweet["text"] for tweet in queue}
    
    # Score all tweets
    scored_tweets = [score_tweet(tweet) for tweet in tweets]
    
    # Add qualified tweets to the queue
    added_count = 0
    for tweet in scored_tweets:
        # Check if the tweet meets minimum score and isn't a duplicate
        if tweet["score"] >= min_score and tweet["text"] not in existing_texts:
            queue.append(tweet)
            existing_texts.add(tweet["text"])
            added_count += 1
    
    # Save updated queue
    save_tweet_queue(queue)
    
    return scored_tweets, added_count

def get_next_tweet_from_queue():
    """Get the next tweet from the queue and remove it"""
    queue = load_tweet_queue()
    
    if not queue:
        return None
    
    # Get the first tweet
    next_tweet = queue.pop(0)
    
    # Save updated queue
    save_tweet_queue(queue)
    
    return next_tweet

def queue_size():
    """Return the number of tweets in the queue"""
    queue = load_tweet_queue()
    return len(queue)

def select_best_tweet(tweets):
    """
    Select the best tweet based on criteria like:
    - Appropriate length (not too short, not hitting character limit)
    - No hashtags (penalize tweets with hashtags)
    - Has the right amount of emojis
    - Good use of capitalization for emphasis
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

def generate_and_queue_tweets(count=5, min_score=12.0):
    """
    Generate multiple tweets, score them, add qualifying ones to the queue,
    and return the best one for immediate posting
    """
    # Generate tweets
    tweets = generate_multiple_tweets(count=count)
    
    if not tweets:
        return None, 0
    
    # Score and queue tweets
    scored_tweets, added_count = score_and_queue_tweets(tweets, min_score)
    
    # Select the best tweet for immediate posting
    best_tweet = select_best_tweet(scored_tweets)
    
    return best_tweet, added_count 