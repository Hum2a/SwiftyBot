import random
from tweet_generator import generate_tweet, generate_trending_tweet

def generate_multiple_tweets(count=5, include_trending=True):
    """Generate multiple tweets with different personality types and return them all"""
    personality_types = [
        "OBSESSED_TEEN", 
        "MUSIC_CRITIC", 
        "CONSPIRACY_THEORIST", 
        "RELUCTANT_FAN",
        "BOOMER_CONFUSED",
        "CORPORATE_SHILL",
        "ECONOMICS_PROFESSOR"
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

def select_best_tweet(tweets):
    """
    Select the best tweet based on criteria like:
    - Appropriate length (not too short, not hitting character limit)
    - Contains hashtags
    - Has the right amount of emojis
    - Good use of capitalization for emphasis
    """
    if not tweets:
        return None
    
    scored_tweets = []
    
    for tweet in tweets:
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
        
        # Hashtag score - tweets with 1-3 hashtags get bonus points
        hashtag_count = text.count('#')
        if 1 <= hashtag_count <= 3:
            score += 5
        
        # Emoji score - some emojis are good, too many are bad
        emoji_count = sum(1 for char in text if ord(char) > 127000)
        if 1 <= emoji_count <= 4:
            score += 5
        elif emoji_count > 4:
            score -= (emoji_count - 4) * 2
        
        # Capitalization for emphasis
        caps_words = sum(1 for word in text.split() if word.isupper() and len(word) > 1)
        if 1 <= caps_words <= 3:
            score += 5
        
        # Irony/humor indicators
        if "..." in text or "…" in text:
            score += 3  # Ellipsis often indicates irony
        if "!" in text and "?" in text:
            score += 3  # Exclamation and question marks together often indicate humor
        
        scored_tweets.append((score, tweet))
    
    # Sort by score and return the highest-scoring tweet
    scored_tweets.sort(reverse=True)
    return scored_tweets[0][1]

def get_optimal_tweet():
    """Generate multiple tweets and select the best one"""
    tweets = generate_multiple_tweets(count=5)
    return select_best_tweet(tweets) 