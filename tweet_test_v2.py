import requests
from config import TWITTER_BEARER_TOKEN

def post_tweet(text):
    url = "https://api.twitter.com/2/tweets"
    headers = {
        "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "text": text
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("Tweet posted successfully!")
    else:
        print(f"Error posting tweet: {response.status_code} - {response.text}")

# Test posting a tweet
post_tweet("Hello, Twitter! This is a test tweet using v2 API.") 