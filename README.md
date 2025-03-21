# SwiftyBot 🤖 Tweet Generator

SwiftyBot is an advanced Twitter bot that generates and posts entertaining tweets with various personalities. It uses OpenAI's GPT models to create funny, ironic, and slightly ridiculous content that captures attention and engagement.

## 🌟 Features

- **Multiple Personality Types**: Choose from 14 different personality profiles and a trending option
- **Intelligent Tweet Scoring**: Automatic evaluation of tweet quality based on multiple factors
- **Tweet Queuing**: Save good tweets for later posting to maximize content usage
- **Duplicate Prevention**: Advanced checks to avoid posting similar content twice
- **Rate Limit Handling**: Smart handling of Twitter API rate limits
- **Manual and Automatic Modes**: Run fully automated or control exactly what gets posted
- **Detailed Logging**: Track generation sessions, posted content, and performance metrics

## 📋 Personality Types

### Taylor Swift Fan Personalities
1. **OBSESSED_TEEN**: 16-year-old diehard Taylor Swift fan with excessive emojis and ALL CAPS
2. **FEMINIST_SWIFTIE**: Links everything to the patriarchy with incorrect feminist terminology
3. **CONSPIRACY_SWIFTIE**: Believes Taylor is sending personal messages through lyrics
4. **CHRONICALLY_ONLINE_FAN**: Spends every waking moment defending Taylor online
5. **TOXIC_STAN**: Attacks anyone who criticizes Taylor, especially men
6. **MIDDLE_AGED_SWIFTIE**: Tries way too hard to fit in with younger fans
7. **DELUSIONAL_SUPERFAN**: Convinced Taylor reads all their tweets

### Socio-Political Personalities
8. **CONSPIRACY_THEORIST**: Believes the government is controlled by lizard people
9. **TECH_BRO_FUTURIST**: Thinks technology will solve every human problem
10. **PSEUDO_INTELLECTUAL**: Uses complex vocabulary to mask nonsensical arguments
11. **DOOMSDAY_PREPPER**: Convinced societal collapse is imminent
12. **CORPORATE_SHILL**: Defends billion-dollar companies as if they're best friends
13. **ARMCHAIR_EXPERT**: Becomes an 'authority' on any topic after 5 minutes of googling
14. **NOSTALGIC_BOOMER**: Believes everything was better "back in their day"

### Special Type
15. **TRENDING**: Generates tweets about current trends with ironic humor

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- Twitter Developer Account with API keys
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SwiftyBot.git
cd SwiftyBot
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file and add your API keys:
     ```
     # Twitter API Credentials
     TWITTER_API_KEY=your_twitter_api_key
     TWITTER_API_SECRET=your_twitter_api_secret
     TWITTER_ACCESS_TOKEN=your_twitter_access_token
     TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
     TWITTER_BEARER_TOKEN=your_twitter_bearer_token
     
     # OpenAI API Credentials
     OPENAI_API_KEY=your_openai_api_key
     ```

### API Keys

#### Twitter API Keys
To get Twitter API keys, you need to:
1. Create a Twitter Developer account at [developer.twitter.com](https://developer.twitter.com/)
2. Create a new project and app in the Developer Portal
3. Apply for Elevated access to get read/write permissions
4. Generate consumer keys and access tokens from the app settings

#### OpenAI API Key
To get an OpenAI API key:
1. Create an account at [platform.openai.com](https://platform.openai.com/)
2. Navigate to the API keys section
3. Create a new secret key
4. Copy the key (it will only be shown once)

## 💻 Usage

### Automatic Mode

Run the bot in automatic mode to post tweets periodically:

```bash
python bot.py
```

The bot will:
1. Generate tweets from random personalities
2. Score and select the best tweets
3. Queue high-quality tweets for later use
4. Post tweets at random intervals (13-38 minutes)
5. Avoid posting duplicates

### Manual Mode

Use manual mode to control exactly which tweets are generated and posted:

```bash
# Interactive mode (menu-driven interface)
python manual_bot.py

# Generate a tweet with a specific personality
python manual_bot.py --personality 8

# Generate a tweet with a specific personality by name
python manual_bot.py --personality CONSPIRACY_THEORIST

# Generate and immediately post a tweet
python manual_bot.py --personality TECH_BRO_FUTURIST --post

# Generate a tweet with a random personality
python manual_bot.py --personality random

# Generate a trending tweet
python manual_bot.py --personality trending
```

### Switching Personalities

Control which personality types are used for generation:

```bash
# List all available personalities
python mode_switcher.py list

# Switch to Taylor Swift mode only
python mode_switcher.py switch --mode taylor

# Switch to socio-political mode only
python mode_switcher.py switch --mode socio

# Use all personalities
python mode_switcher.py switch --mode all

# Generate sample tweets to preview
python mode_switcher.py sample --mode socio --count 5
```

### Managing the Tweet Queue

View and manage queued tweets:

```bash
# View all tweets in the queue
python queue_manager.py show

# Remove a specific tweet (by position)
python queue_manager.py remove --index 3

# Clear the entire queue
python queue_manager.py clear

# Reorder queue by score (highest first)
python queue_manager.py reorder

# Clean duplicates from the queue
python queue_manager.py clean
```

## 📊 Tweet Scoring System

Tweets are scored based on multiple factors:

- **Length**: Optimal tweets are 100-240 characters (10 points)
- **Hashtags**: Heavily penalized (-10 points per hashtag)
- **Emojis**: 1-4 emojis are rewarded (5 points), more are penalized
- **Capitalization**: Strategic use of CAPS words (5 points for 1-3 words)
- **Irony Indicators**: Ellipses and mixed punctuation (3 points each)

Only tweets scoring above the threshold (default: 9.0) are queued for posting.

## 📁 Project Structure

- `bot.py` - Main automatic bot script
- `manual_bot.py` - Manual tweet generation and posting
- `tweet_generator.py` - Tweet content generation using OpenAI
- `tweet_selector.py` - Tweet scoring, selection, and queue management
- `config.py` - Configuration settings and personality definitions
- `mode_switcher.py` - Tool to switch between personality modes
- `queue_manager.py` - Tool to manage the tweet queue
- `utils.py` - Utility functions

## 📝 Logs and Records

- `Tweeted_tweets.txt` - Record of all previously posted tweets
- `All_generated_tweets.txt` - Detailed log of generation sessions
- `log.txt` - Bot activity log

## 🔧 Configuration

Edit `config.py` to customize:

- Personality definitions
- Default system prompts
- Tweet interval times
- API configuration

## ⚠️ Rate Limits

The bot intelligently handles Twitter API rate limits by:
- Spacing out API calls
- Using local checks where possible
- Backing off when limits are reached
- Maintaining a queue of pre-generated content

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [OpenAI](https://openai.com/) for the GPT API
- [Tweepy](https://www.tweepy.org/) for Twitter API integration 