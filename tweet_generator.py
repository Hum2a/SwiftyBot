import openai
from config import OPENAI_API_KEY, SYSTEM_PROMPTS

openai.api_key = OPENAI_API_KEY

def generate_tweet(personality_type="OBSESSED_TEEN"):
    """Generate a tweet using OpenAI's API with specified personality type"""
    try:
        # Enhanced prompt for more cringey, man-hating Taylor Swift fan content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[personality_type]},
                {"role": "user", "content": "Generate a tweet as a cringey Taylor Swift fan who irrationally hates men (especially her exes) and makes easily disproven claims about her success or achievements. The tweet should be funny because of how delusional and over-the-top it is. Make it feel like it could go viral for being both hilarious and slightly rage-inducing to the average Twitter user. Keep it under 280 characters. DO NOT include any hashtags in your response. Please also don't include quotation marks in your response."}
            ],
            max_tokens=100,
            temperature=0.9  # Slightly higher temperature for more creative outputs
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating tweet: {e}")
        return None

def generate_trending_tweet():
    """Generate a tweet that references current trends with toxic fan energy"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a toxic, chronically online Taylor Swift fan who hates all men, especially her exes. You believe Taylor is a literal goddess who can do no wrong, and you make ridiculous, easily disproven claims about her achievements and success. You're extremely defensive of Taylor and attack anyone who criticizes her."},
                {"role": "user", "content": "Generate a tweet as a cringey Taylor Swift fan that references current events or controversies. Include some easily disproven claim about Taylor's success and a negative comment about men (especially if it's one of her exes). Make it obviously delusional but funny in how over-the-top it is. Keep it under 280 characters. DO NOT include any hashtags in your response. Please also don't include quotation marks in your response."}
            ],
            max_tokens=100,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating trending tweet: {e}")
        return None 