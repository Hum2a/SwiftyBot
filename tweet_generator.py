import openai
from config import OPENAI_API_KEY, SYSTEM_PROMPTS

openai.api_key = OPENAI_API_KEY

def is_taylor_swift_personality(personality_type):
    """Check if the personality type is Taylor Swift related"""
    taylor_swift_types = [
        "OBSESSED_TEEN", 
        "FEMINIST_SWIFTIE", 
        "CONSPIRACY_SWIFTIE", 
        "CHRONICALLY_ONLINE_FAN",
        "TOXIC_STAN",
        "MIDDLE_AGED_SWIFTIE",
        "DELUSIONAL_SUPERFAN"
    ]
    return personality_type in taylor_swift_types

def generate_tweet(personality_type="CONSPIRACY_THEORIST"):
    """Generate a tweet using OpenAI's API with specified personality type"""
    try:
        # Determine if this is a Taylor Swift personality or socio-political
        is_taylor = is_taylor_swift_personality(personality_type)
        
        # Create the appropriate prompt based on personality type
        if is_taylor:
            user_prompt = "Generate a tweet as a cringey Taylor Swift fan who irrationally hates men (especially her exes) and makes easily disproven claims about her success or achievements. The tweet should be funny because of how delusional and over-the-top it is. Make it feel like it could go viral for being both hilarious and slightly rage-inducing to the average Twitter user. Keep it under 280 characters. DO NOT include any hashtags in your response. Please also don't include quotation marks in your response."
        else:
            user_prompt = "Generate a tweet with a ridiculous socio-political take that would be funny and easy to make fun of. The tweet should contain absurd claims, logical fallacies, or completely misunderstood facts. Make it feel like it could go viral for being both hilarious and slightly rage-inducing to the average Twitter user. Keep it under 280 characters. DO NOT include any hashtags in your response. Please also don't include quotation marks in your response."
        
        # Enhanced prompt for more ironic and humorous content
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[personality_type]},
                {"role": "user", "content": user_prompt}
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
                {"role": "user", "content": "Generate a tweet with a ridiculous hot take on a current trend, news event, or popular topic. Make it ironic, funny, and slightly provocative. The tweet should feel like it was written by someone who's extremely online and has absurd opinions. Keep it under 280 characters. DO NOT include any hashtags in your response. Please also don't include quotation marks in your response."}
            ],
            max_tokens=100,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating trending tweet: {e}")
        return None 