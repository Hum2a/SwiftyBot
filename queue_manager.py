import json
import argparse
from tweet_selector import (
    load_tweet_queue, 
    save_tweet_queue, 
    clean_queue_of_duplicates,
    get_previously_tweeted_texts
)

def display_queue():
    """Display all tweets in the queue"""
    queue = load_tweet_queue()
    
    if not queue:
        print("Queue is empty.")
        return
    
    print(f"\n=== TWEET QUEUE ({len(queue)} tweets) ===\n")
    
    for i, tweet in enumerate(queue):
        score_info = f"Score: {tweet.get('score', 'N/A'):.2f}" if 'score' in tweet else ''
        personality = tweet.get('personality', 'UNKNOWN')
        
        print(f"[{i+1}] - {personality} {score_info}")
        print(tweet.get('text', 'No text available'))
        print("-" * 50)

def remove_tweet(index):
    """Remove a tweet from the queue by index"""
    queue = load_tweet_queue()
    
    if not queue:
        print("Queue is empty.")
        return
    
    try:
        index = int(index) - 1  # Convert to 0-based index
        if index < 0 or index >= len(queue):
            print(f"Invalid index. Please provide a number between 1 and {len(queue)}.")
            return
        
        removed = queue.pop(index)
        save_tweet_queue(queue)
        
        print(f"Removed tweet: {removed.get('text', 'No text available')}")
        print(f"Queue now has {len(queue)} tweets.")
    except ValueError:
        print("Please provide a valid number.")

def clear_queue():
    """Clear the entire queue"""
    save_tweet_queue([])
    print("Queue has been cleared.")

def reorder_queue():
    """Reorder queue by score (highest first)"""
    queue = load_tweet_queue()
    
    if not queue:
        print("Queue is empty.")
        return
    
    # Sort by score (if available)
    queue.sort(key=lambda x: x.get('score', 0), reverse=True)
    save_tweet_queue(queue)
    
    print("Queue has been reordered by score (highest first).")

def clean_duplicates(api_credentials=None):
    """Remove duplicates from the queue"""
    # This first checks local records
    queue = load_tweet_queue()
    original_length = len(queue)
    
    previously_tweeted = get_previously_tweeted_texts()
    queue = [tweet for tweet in queue if tweet["text"] not in previously_tweeted]
    
    # Check if we need to connect to Twitter API
    api_client = None
    if api_credentials:
        try:
            import tweepy
            # Parse credentials
            credentials = api_credentials.split(',')
            if len(credentials) == 4:
                api_key, api_secret, access_token, access_token_secret = credentials
                auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
                api_client = tweepy.Client(
                    consumer_key=api_key,
                    consumer_secret=api_secret,
                    access_token=access_token,
                    access_token_secret=access_token_secret
                )
                print("Connected to Twitter API")
            else:
                print("Invalid API credentials format. Expected: api_key,api_secret,access_token,access_token_secret")
        except ImportError:
            print("Tweepy not available, skipping API check")
        except Exception as e:
            print(f"Error connecting to Twitter API: {e}")
    
    # Use the function that checks both local and Twitter
    removed_count = clean_queue_of_duplicates(api_client)
    
    print(f"Removed {removed_count} duplicate tweets from queue.")
    print(f"Queue now has {len(load_tweet_queue())} tweets.")

def main():
    parser = argparse.ArgumentParser(description="Manage the tweet queue")
    parser.add_argument('action', choices=['show', 'remove', 'clear', 'reorder', 'clean'], 
                        help='Action to perform on the queue')
    parser.add_argument('--index', type=int, help='Index of tweet to remove (1-based)')
    parser.add_argument('--api-credentials', help='Twitter API credentials in format: api_key,api_secret,access_token,access_token_secret')
    
    args = parser.parse_args()
    
    if args.action == 'show':
        display_queue()
    elif args.action == 'remove':
        if args.index is None:
            print("Please provide an index with --index")
            return
        remove_tweet(args.index)
    elif args.action == 'clear':
        clear_queue()
    elif args.action == 'reorder':
        reorder_queue()
    elif args.action == 'clean':
        clean_duplicates(args.api_credentials)

if __name__ == "__main__":
    main() 