import argparse
import tweepy
import time
from datetime import datetime
import os
import sys
from config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET,
    SYSTEM_PROMPTS
)
from tweet_generator import generate_tweet, is_taylor_swift_personality
from tweet_selector import score_tweet, get_previously_tweeted_texts
from utils import log_activity

class ManualBot:
    def __init__(self):
        self.client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )
        self.previously_tweeted = get_previously_tweeted_texts()
        log_activity(f"Loaded {len(self.previously_tweeted)} previously tweeted texts")
        
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
    
    def check_duplicate(self, tweet_text):
        """Check if a tweet is a duplicate"""
        return tweet_text in self.previously_tweeted
    
    def post_tweet(self, tweet_text, personality):
        """Post a tweet to Twitter"""
        try:
            # Check for duplicates
            if self.check_duplicate(tweet_text):
                print("\n⚠️ WARNING: This tweet appears to be a duplicate of a previously posted tweet!")
                confirm = input("Post anyway? (y/n): ").strip().lower()
                if confirm != 'y':
                    return False
            
            # Post the tweet
            response = self.client.create_tweet(text=tweet_text)
            
            # Save the tweet
            self.save_tweet(tweet_text, personality)
            
            print(f"\n✅ Tweet posted successfully!")
            log_activity(f"Tweet posted successfully: {tweet_text}")
            return True
        except Exception as e:
            print(f"\n❌ Error posting tweet: {e}")
            log_activity(f"Error posting tweet: {e}")
            return False

def list_personalities():
    """List all available personality types with descriptions"""
    # Group personalities
    taylor_personalities = [
        "OBSESSED_TEEN", 
        "FEMINIST_SWIFTIE", 
        "CONSPIRACY_SWIFTIE", 
        "CHRONICALLY_ONLINE_FAN",
        "TOXIC_STAN",
        "MIDDLE_AGED_SWIFTIE",
        "DELUSIONAL_SUPERFAN"
    ]
    
    socio_political_personalities = [
        "CONSPIRACY_THEORIST",
        "TECH_BRO_FUTURIST",
        "PSEUDO_INTELLECTUAL",
        "DOOMSDAY_PREPPER",
        "CORPORATE_SHILL",
        "ARMCHAIR_EXPERT",
        "NOSTALGIC_BOOMER"
    ]
    
    print("\n=== AVAILABLE PERSONALITY TYPES ===\n")
    
    print("TAYLOR SWIFT PERSONALITIES:")
    for i, personality in enumerate(taylor_personalities):
        print(f"  {i+1}. {personality}")
        # Print a short description
        description = SYSTEM_PROMPTS[personality].split('.')[0]
        print(f"     {description}.")
        print()
    
    print("\nSOCIO-POLITICAL PERSONALITIES:")
    for i, personality in enumerate(socio_political_personalities):
        print(f"  {i+1+len(taylor_personalities)}. {personality}")
        # Print a short description
        description = SYSTEM_PROMPTS[personality].split('.')[0]
        print(f"     {description}.")
        print()
    
    print("\nTRENDING:")
    print(f"  {len(taylor_personalities) + len(socio_political_personalities) + 1}. TRENDING")
    print("     Generates a tweet about current trends with ironic humor.")
    print()

def get_personality_by_number(number):
    """Get personality type by its number in the list"""
    all_personalities = [
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
    
    if number < 1 or number > len(all_personalities) + 1:
        return None
    
    if number == len(all_personalities) + 1:
        return "TRENDING"
    
    return all_personalities[number - 1]

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def interactive_mode():
    """Run the bot in interactive mode"""
    bot = ManualBot()
    
    while True:
        clear_screen()
        print("=== MANUAL TWITTER BOT ===")
        print("1. Generate a tweet")
        print("2. List personality types")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            # Generate a tweet
            clear_screen()
            print("=== GENERATE A TWEET ===\n")
            
            # Show personality options
            list_personalities()
            
            # Get personality choice
            personality_num = input("\nSelect a personality (1-15) or 'r' for random: ").strip().lower()
            
            if personality_num == 'r':
                import random
                personality_num = random.randint(1, 15)
            else:
                try:
                    personality_num = int(personality_num)
                except ValueError:
                    print("\n❌ Invalid input. Please enter a number between 1 and 15.")
                    input("\nPress Enter to continue...")
                    continue
            
            personality = get_personality_by_number(personality_num)
            
            if not personality:
                print("\n❌ Invalid personality number.")
                input("\nPress Enter to continue...")
                continue
            
            # Generate the tweet
            print(f"\nGenerating tweet with personality: {personality}...")
            
            if personality == "TRENDING":
                from tweet_generator import generate_trending_tweet
                tweet_text = generate_trending_tweet()
            else:
                tweet_text = generate_tweet(personality)
            
            if not tweet_text:
                print("\n❌ Failed to generate tweet.")
                input("\nPress Enter to continue...")
                continue
            
            # Score the tweet
            tweet_data = {"text": tweet_text, "personality": personality}
            scored_tweet = score_tweet(tweet_data)
            
            # Display the tweet
            clear_screen()
            print("=== GENERATED TWEET ===\n")
            print(f"Personality: {personality}")
            print(f"Score: {scored_tweet['score']:.2f}")
            print("\nTweet:")
            print("-" * 50)
            print(tweet_text)
            print("-" * 50)
            
            # Check for duplicates
            if bot.check_duplicate(tweet_text):
                print("\n⚠️ WARNING: This tweet appears to be a duplicate of a previously posted tweet!")
            
            # Ask what to do with the tweet
            print("\nWhat would you like to do?")
            print("1. Post this tweet")
            print("2. Generate a new tweet")
            print("3. Return to main menu")
            
            action = input("\nEnter your choice (1-3): ").strip()
            
            if action == '1':
                # Post the tweet
                bot.post_tweet(tweet_text, personality)
                input("\nPress Enter to continue...")
            elif action == '2':
                # Generate a new tweet (loop back)
                continue
            else:
                # Return to main menu
                continue
            
        elif choice == '2':
            # List personality types
            clear_screen()
            list_personalities()
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            # Exit
            print("\nExiting Manual Bot. Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 3.")
            input("\nPress Enter to continue...")

def command_line_mode(args):
    """Run the bot in command line mode"""
    bot = ManualBot()
    
    # Get the personality
    if args.personality.lower() == 'random':
        import random
        personality_num = random.randint(1, 15)
        personality = get_personality_by_number(personality_num)
    elif args.personality.lower() == 'trending':
        personality = "TRENDING"
    elif args.personality.isdigit():
        personality_num = int(args.personality)
        personality = get_personality_by_number(personality_num)
    else:
        # Try to match by name
        if args.personality.upper() in SYSTEM_PROMPTS:
            personality = args.personality.upper()
        else:
            print(f"❌ Unknown personality: {args.personality}")
            return
    
    print(f"Generating tweet with personality: {personality}...")
    
    # Generate the tweet
    if personality == "TRENDING":
        from tweet_generator import generate_trending_tweet
        tweet_text = generate_trending_tweet()
    else:
        tweet_text = generate_tweet(personality)
    
    if not tweet_text:
        print("❌ Failed to generate tweet.")
        return
    
    # Score the tweet
    tweet_data = {"text": tweet_text, "personality": personality}
    scored_tweet = score_tweet(tweet_data)
    
    # Display the tweet
    print(f"\nPersonality: {personality}")
    print(f"Score: {scored_tweet['score']:.2f}")
    print("\nTweet:")
    print("-" * 50)
    print(tweet_text)
    print("-" * 50)
    
    # Check for duplicates
    if bot.check_duplicate(tweet_text):
        print("\n⚠️ WARNING: This tweet appears to be a duplicate of a previously posted tweet!")
    
    # Post if requested
    if args.post:
        bot.post_tweet(tweet_text, personality)

def main():
    parser = argparse.ArgumentParser(description="Manual Twitter Bot")
    parser.add_argument('--personality', '-p', 
                        help='Personality to use (number, name, "random", or "trending")')
    parser.add_argument('--post', '-P', action='store_true',
                        help='Post the generated tweet')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # If no arguments or interactive flag, run in interactive mode
    if len(sys.argv) == 1 or args.interactive:
        interactive_mode()
    else:
        # Command line mode
        if not args.personality:
            print("❌ Please specify a personality with --personality")
            return
        
        command_line_mode(args)

if __name__ == "__main__":
    main() 