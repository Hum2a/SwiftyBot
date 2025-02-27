import random
from datetime import datetime
import time
from config import MIN_TWEET_INTERVAL, MAX_TWEET_INTERVAL

def get_random_interval():
    """Get a random interval between tweets"""
    return random.randint(MIN_TWEET_INTERVAL, MAX_TWEET_INTERVAL)

def log_activity(message):
    """Log bot activity with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}") 