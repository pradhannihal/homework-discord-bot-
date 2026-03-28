# Homework Helper Bot

> A Discord bot built by an older brother to help keep track of his younger brother's homework and studies.

---

## The Story Behind It

My little brother and I both use Discord to play games together. I wanted a way to stay connected with him and make sure he was keeping up with school, so I built this bot. Instead of just texting him every day, I thought it would be cooler to automate it through something we both already use. The bot lets me check in on his homework, see what subjects he's struggling with, and gives him an AI tutor he can ask questions to anytime. It's my way of looking out for him as an older brother.

---

## What It Does

- Automatically asks your sibling if they finished their homework every day at 6PM
- DMs you when they reply so you always know what's going on
- If they say "no", follows up to find out what subject they're stuck on and relays it to you
- Answers their questions using AI with conversation memory so it feels natural
- Logs every subject they ask about so you can spot patterns over time
- Gives you a report on what subjects they struggle with most

---

## Commands

| Command | Who can use it | What it does |
|---|---|---|
| `!homework` | Owner only | Manually asks your sibling if they finished homework |
| `!ask [question]` | Anyone | Asks the AI a question (remembers the full conversation) |
| `!tutor [question]` | Anyone | Gets a simple step-by-step explanation suited for kids |
| `!report` | Owner only | Shows which subjects your sibling struggled with most |

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/pradhannihal/homework-discord-bot-.git
cd homework-discord-bot-
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file
Copy `.env.example` to `.env` and fill in your values:
```
GROQ_API_KEY=your_groq_api_key
DISCORD_TOKEN=your_discord_bot_token
MY_ID=your_discord_user_id
LILBRO_ID=brothers_discord_user_id
```

### 4. Run the bot
```bash
python bot.py
```

---

## Built With

- [Discord.py](https://discordpy.readthedocs.io/) — Discord bot framework
- [Groq API](https://groq.com/) — AI responses using llama-3.3-70b-versatile
- Python 3

---

## Future Plans

- Struggle detection — auto alert when the same subject comes up multiple times in one day
- Homework streak tracking — see patterns over time
- Practice problems — generate quiz questions on any subject
- Persistent chat history — remember conversations across bot restarts
