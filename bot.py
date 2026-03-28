# ── IMPORTS ───────────────────────────────────────────────────────────────────
import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os
from groq import Groq
import datetime
from collections import Counter
import json


# ── CONFIGURATION & ENVIRONMENT ───────────────────────────────────────────────
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
token = os.getenv('DISCORD_TOKEN')
my_id = os.getenv('MY_ID')
lilbro_id = os.getenv('LILBRO_ID')


print(f"My ID: {my_id}")
print(f"Brother ID: {lilbro_id}")

if my_id is None:
    raise RuntimeError(
        "MY_ID is not set. Copy .env.example to .env and set your ID, or set the environment variable MY_ID."
    )
if lilbro_id is None:
    raise RuntimeError(
        "LILBRO_ID is not set. Copy .env.example to .env and set your brother's ID, or set the environment variable LILBRO_ID."
    )
if token is None:
    raise RuntimeError(
        "DISCORD_TOKEN is not set. Copy .env.example to .env and set your token, or set the environment variable DISCORD_TOKEN."
    )
if groq_api_key is None:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add your Groq API key to your .env file."
    )


# ── CONSTANTS ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, 'homework_responses.json')
QUESTION_LOG_FILE = os.path.join(BASE_DIR, 'homework_questions.json')
chat_history = {}
waiting_for_response = {}  # Tracks which users we're waiting for a homework response from


# ── BOT SETUP ─────────────────────────────────────────────────────────────────
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)
groq_client = Groq(api_key=groq_api_key)


# ── AI HELPER FUNCTIONS ───────────────────────────────────────────────────────

def tag_subject(question):
    """Uses AI to identify the subject of a homework question."""
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that identifies the subject of a homework question. Respond with only the subject name (e.g., 'math', 'science', 'history') based on the following question: "},
            {"role": "user", "content": question}
        ],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content.strip().lower()

def ask_ai(user_id, prompt):
    """Sends a prompt to the AI with per-user chat history (last 20 messages)."""
    if user_id not in chat_history:
        chat_history[user_id] = []

    chat_history[user_id].append({"role": "user", "content": prompt})

    if len(chat_history[user_id]) > 20:
        chat_history[user_id] = chat_history[user_id][-20:]

    message = [
        {"role": "system", "content": "You are a helpful assistant that answers questions in a friendly and concise manner."},
        *chat_history[user_id]
    ]

    chat_completion = groq_client.chat.completions.create(
        messages=message,
        model="llama-3.3-70b-versatile"
    )

    reply = chat_completion.choices[0].message.content
    chat_history[user_id].append({"role": "assistant", "content": reply})
    return reply

def tutor_ai(question):
    """Answers a question in simple terms for an elementary school student."""
    chat_completion = groq_client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a friendly tutor helping an elementary school student. Always explain things in very simple words a 10 year old can understand. Break down every answer into small easy steps. Use fun examples from everyday life. Never use complicated words without explaining them first. Keep answers short and encouraging."},
            {"role": "user", "content": question}
        ],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content.strip()


# ── DATA HELPER FUNCTIONS ─────────────────────────────────────────────────────

def save_homework_response(answer):
    """Saves brother's yes/no homework response to JSON."""
    print(f"Saving response: {answer}")
    print(f"Saving to: {os.path.abspath(LOG_FILE)}")
    try:
        with open(LOG_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append({
        "date": str(datetime.date.today()),
        "answer": answer
    })

    with open(LOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def save_question(question):
    """Tags and saves a homework question to JSON."""
    subject = tag_subject(question)

    try:
        with open(QUESTION_LOG_FILE, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append({
        "date": str(datetime.date.today()),
        "question": question,
        "subject": subject
    })

    with open(QUESTION_LOG_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# ── COMMANDS ──────────────────────────────────────────────────────────────────

@bot.command()
async def homework(ctx):
    """Owner only: DMs brother asking if he finished his homework."""
    if str(ctx.author.id) != my_id:
        await ctx.send("sorry, only the owner can use this command")
        return

    brother = await bot.fetch_user(int(lilbro_id))
    await brother.send("Bivan did you finish your homework? Reply with 'yes' or 'no'.")
    await ctx.send(" Asked your brother about homework! Waiting for his response")

@bot.command()
async def ask(ctx, *, question):
    """Asks the AI a question with chat history."""
    try:
        await ctx.send("Thinking...")
        response = ask_ai(str(ctx.author.id), question)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def tutor(ctx, *, question):
    """Asks the AI tutor to explain something simply."""
    try:
        await ctx.send("Let me explain that for you...")
        response = tutor_ai(question)
        await ctx.send(response)
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def report(ctx):
    """Owner only: Shows which subjects brother struggled with most."""
    if str(ctx.author.id) != my_id:
        await ctx.send("sorry, only the owner can use this command")
        return

    try:
        with open(QUESTION_LOG_FILE, 'r') as f:
            data = json.load(f)
            print(f"loaded {len(data)} entries")
    except FileNotFoundError:
        await ctx.send("No homework responses found.")
        return

    subject = []
    for entry in data:
        print(f"entry: {entry}")
        if 'subject' in entry:
            subject.append(entry['subject'])

    counts = Counter(subject)
    print(f"counts: {counts}")
    await ctx.send(f"Brother struggled most with: {counts.most_common()}")


# ── SCHEDULED TASKS ───────────────────────────────────────────────────────────

@tasks.loop(time=datetime.time(hour=18, minute=0, second=0))
async def daily_homework_reminder():
    """Sends brother a daily homework reminder at 6:00 PM UTC."""
    brother = await bot.fetch_user(int(lilbro_id))
    await brother.send("Hey! Did you finish your homework today? Reply with 'yes' or 'no'")
    owner = await bot.fetch_user(int(my_id))
    await owner.send(" Sent your brother the homework reminder!")


# ── EVENTS ────────────────────────────────────────────────────────────────────

@bot.event
async def on_member_join(member):
    """Welcomes new members with a DM."""
    await member.send(f"Welcome to the server, {member.name}!")

@bot.event
async def on_message(message):
    """Handles incoming messages: forwards brother's DMs and responds to all DMs with AI."""
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel) and str(message.author.id) == lilbro_id:
        owner = await bot.fetch_user(int(my_id))
    
        if str(message.author.id) in waiting_for_response:
            await owner.send(f"brother is stuck on: {message.content}")
            del waiting_for_response[str(message.author.id)]
            return 
        
        elif message.content.lower() == "yes":
            await owner.send(f"brother finished his homework!") 
            save_homework_response("Yes")
            await message.channel.send("Great job! Keep it up!")
            return
        elif message.content.lower() == "no":
            await owner.send(f"brother did not finish his homework")
            save_homework_response("No")
            await message.channel.send("What do you need help with?")
            waiting_for_response[str(message.author.id)] = True
            return
        else:
            save_question(message.content)

    if isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            response = ask_ai(str(message.author.id), message.content)
        await message.channel.send(response)

    await bot.process_commands(message)

@bot.event
async def on_ready():
    """Starts scheduled tasks when the bot is ready."""
    daily_homework_reminder.start()
    print(f"ready, {bot.user.name}")


# ── RUN ───────────────────────────────────────────────────────────────────────
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
        
