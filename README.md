# Taylor Swift Fan Twitter Bot

A Twitter bot that simulates a 15-year-old Taylor Swift fan, generating and posting tweets using OpenAI's GPT-3.5.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API credentials
4. Run the bot:
   ```bash
   python bot.py
   ```

## Configuration

- Edit `config.py` to modify bot behavior
- Adjust tweet intervals in `config.py`
- Modify the bot's personality by editing the `SYSTEM_PROMPT`

## Features

- Generates tweets using GPT-3.5
- Random posting intervals
- Activity logging
- Error handling 