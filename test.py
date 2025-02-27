from tweet_generator import generate_tweet
from utils import log_activity
from datetime import datetime
from config import SYSTEM_PROMPTS

def test_tweet_generation(num_tweets=1, personality_type="OBSESSED_TEEN"):
    log_activity(f"Testing tweet generation for {num_tweets} tweets using {personality_type} personality...")
    
    for i in range(num_tweets):
        log_activity(f"\nGenerating tweet {i+1}/{num_tweets}")
        tweet = generate_tweet(personality_type)
        if tweet:
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Print to console
            log_activity("Generated tweet:")
            print("\n---Tweet Preview---")
            print(tweet)
            print("---End Preview---\n")
            print(f"Character count: {len(tweet)}/280")
            
            # Save to file
            with open("Swifty_Tweets.txt", "a", encoding="utf-8") as f:
                f.write(f"\n[{timestamp}] - {personality_type}\n")
                f.write(tweet)
                f.write("\n" + "-"*50 + "\n")
            
            log_activity("Tweet saved to Swifty_Tweets.txt")
        else:
            log_activity("Failed to generate tweet")

def print_personality_options():
    print("\nAvailable personality types:")
    for i, personality in enumerate(SYSTEM_PROMPTS.keys(), 1):
        print(f"{i}. {personality.replace('_', ' ').title()}")

if __name__ == "__main__":
    while True:
        print_personality_options()
        try:
            personality_choice = int(input("\nSelect a personality type (enter number): "))
            if 1 <= personality_choice <= len(SYSTEM_PROMPTS):
                personality_type = list(SYSTEM_PROMPTS.keys())[personality_choice - 1]
                num_tweets = int(input("How many tweets would you like to generate? (enter a number): "))
                if num_tweets > 0:
                    test_tweet_generation(num_tweets, personality_type)
                    break
                else:
                    print("Please enter a positive number.")
            else:
                print("Please select a valid personality type number.")
        except ValueError:
            print("Please enter valid numbers.") 