import openai
from config import OPENAI_API_KEY, SYSTEM_PROMPTS

openai.api_key = OPENAI_API_KEY

def generate_tweet(personality_type="OBSESSED_TEEN"):
    """Generate a tweet using OpenAI's API with specified personality type"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[personality_type]},
                {"role": "user", "content": "Generate a tweet about Taylor Swift"}
            ],
            max_tokens=100,
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating tweet: {e}")
        return None 