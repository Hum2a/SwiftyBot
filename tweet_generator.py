import openai
from config import OPENAI_API_KEY, SYSTEM_PROMPTS

openai.api_key = OPENAI_API_KEY

def generate_tweet(personality_type="OBSESSED_TEEN"):
    """Generate a tweet using OpenAI's API with specified personality type"""
    try:
        # Enhanced prompt for more ironic and humorous content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[personality_type]},
                {"role": "user", "content": "Generate a tweet about Taylor Swift that's extremely ironic, funny, and slightly controversial. The tweet should appeal to Gen Z humor while maintaining a layer of self-awareness. Make it feel like it could go viral for being both hilarious and slightly rage-inducing to the average Twitter user. Keep it under 280 characters."}
            ],
            max_tokens=100,
            temperature=0.9  # Slightly higher temperature for more creative outputs
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating tweet: {e}")
        return None

def generate_trending_tweet():
    """Generate a tweet that references current trends with ironic humor"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a master of internet culture and Gen Z humor. You create tweets that perfectly balance irony, humor, and cultural references. Your tweets often go viral because they capture the zeitgeist while maintaining a layer of self-awareness."},
                {"role": "user", "content": "Generate a tweet about Taylor Swift that references current trends or controversies. Make it ironic, funny, and slightly provocative. The tweet should feel like it was written by someone who's extremely online. Keep it under 280 characters. Please also don't include quotation marks in your response."}
            ],
            max_tokens=100,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating trending tweet: {e}")
        return None 