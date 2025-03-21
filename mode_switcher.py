import argparse
import json
import os
from tweet_selector import generate_multiple_tweets, select_best_tweet

def list_personalities():
    """List all available personality types"""
    from config import SYSTEM_PROMPTS
    
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
    
    print("\nSOCIO-POLITICAL PERSONALITIES:")
    for i, personality in enumerate(socio_political_personalities):
        print(f"  {i+1+len(taylor_personalities)}. {personality}")
    
    print("\nTRENDING:")
    print(f"  {len(taylor_personalities) + len(socio_political_personalities) + 1}. TRENDING")

def update_tweet_selector(mode):
    """Update the tweet_selector.py file to use the specified mode"""
    file_path = "tweet_selector.py"
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Find the personality_types list
    if mode == "taylor":
        # Use only Taylor Swift personalities
        new_content = content.replace(
            "# personality_types = all_personality_types[7:]  # Skip the Taylor Swift personalities", 
            "personality_types = all_personality_types[:7]  # Only use Taylor Swift personalities"
        )
        new_content = new_content.replace(
            "personality_types = all_personality_types", 
            "# personality_types = all_personality_types"
        )
    elif mode == "socio":
        # Use only socio-political personalities
        new_content = content.replace(
            "# personality_types = all_personality_types[7:]  # Skip the Taylor Swift personalities", 
            "personality_types = all_personality_types[7:]  # Skip the Taylor Swift personalities"
        )
        new_content = new_content.replace(
            "personality_types = all_personality_types", 
            "# personality_types = all_personality_types"
        )
    else:  # "all"
        # Use all personalities
        new_content = content.replace(
            "personality_types = all_personality_types[:7]  # Only use Taylor Swift personalities", 
            "# personality_types = all_personality_types[:7]  # Only use Taylor Swift personalities"
        )
        new_content = content.replace(
            "personality_types = all_personality_types[7:]  # Skip the Taylor Swift personalities", 
            "# personality_types = all_personality_types[7:]  # Skip the Taylor Swift personalities"
        )
        new_content = new_content.replace(
            "# personality_types = all_personality_types", 
            "personality_types = all_personality_types"
        )
    
    with open(file_path, 'w') as file:
        file.write(new_content)
    
    print(f"Updated tweet_selector.py to use {mode.upper()} mode")

def generate_sample_tweets(count=3, mode=None):
    """Generate sample tweets to preview the current mode"""
    if mode:
        update_tweet_selector(mode)
    
    print(f"\nGenerating {count} sample tweets...\n")
    tweets = generate_multiple_tweets(count=count, include_trending=True)
    
    for i, tweet in enumerate(tweets):
        personality = tweet["personality"]
        text = tweet["text"]
        print(f"[{i+1}] - {personality}")
        print(text)
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(description="Switch between Taylor Swift and socio-political tweet modes")
    parser.add_argument('action', choices=['list', 'switch', 'sample'], 
                        help='Action to perform: list personalities, switch modes, or generate sample tweets')
    parser.add_argument('--mode', choices=['taylor', 'socio', 'all'], 
                        help='Mode to switch to: taylor (Swift only), socio (socio-political only), or all (both)')
    parser.add_argument('--count', type=int, default=3,
                        help='Number of sample tweets to generate (default: 3)')
    
    args = parser.parse_args()
    
    if args.action == 'list':
        list_personalities()
    elif args.action == 'switch':
        if not args.mode:
            print("Please specify a mode with --mode (taylor, socio, or all)")
            return
        update_tweet_selector(args.mode)
    elif args.action == 'sample':
        generate_sample_tweets(count=args.count, mode=args.mode)

if __name__ == "__main__":
    main() 