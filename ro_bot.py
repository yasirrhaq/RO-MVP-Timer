import discord
from discord.ext import tasks, commands
import datetime
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
THREAD_ID = 1318241926645813371  # Replace with your channel (or thread) ID
MENTION_ID = 290861180468199435

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", description="RO MVP Timer", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    mvp_reminder.start()
    mini_reminder.start()

# MVP Reminder: scheduled every 2 hours (spawns at 01:00, 03:00, 05:00, etc.)
@tasks.loop(hours=2)
async def mvp_reminder():
    channel = bot.get_channel(THREAD_ID)
    if channel:
        mention = f"<@{MENTION_ID}>"
        await channel.send(f"**Gas cepet MVP udah Spawn sebelum dihabiskan {mention}!**")

@mvp_reminder.before_loop
async def before_mvp():
    await bot.wait_until_ready()
    now = datetime.datetime.now()
    offset = 3600  # Offset of 1 hour so that spawns start at 01:00 instead of 00:00.
    seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
    # Calculate next spawn based on a 2h (7200 sec) interval with an offset.
    next_spawn_seconds = (((seconds_since_midnight - offset) // 7200) + 1) * 7200 + offset
    next_spawn = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=next_spawn_seconds)
    delay = (next_spawn - now).total_seconds()
    print(f"MVP reminder will start in {delay:.0f} seconds, at {next_spawn}.")
    await asyncio.sleep(delay)

# Mini Reminder: scheduled every 30 minutes (at :00 and :30 marks)
@tasks.loop(minutes=30)
async def mini_reminder():
    channel = bot.get_channel(THREAD_ID)
    if channel:
        mention = f"<@{MENTION_ID}>"
        await channel.send(f"**Gas cepet Mini udah Spawn sebelum dihabiskan {mention}!**")

@mini_reminder.before_loop
async def before_mini():
    await bot.wait_until_ready()
    now = datetime.datetime.now()
    if now.minute < 30:
        next_spawn = now.replace(minute=30, second=0, microsecond=0)
    else:
        next_spawn = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    delay = (next_spawn - now).total_seconds()
    print(f"Mini reminder will start in {delay:.0f} seconds, at {next_spawn}.")
    await asyncio.sleep(delay)

# Helper function for the MVP timer command using the new offset calculation
def get_next_mvp_time():
    now = datetime.datetime.now()
    offset = 3600  # 1-hour offset so that MVP spawns occur at 01:00, 03:00, etc.
    seconds_since_midnight = now.hour * 3600 + now.minute * 60 + now.second
    next_spawn_seconds = (((seconds_since_midnight - offset) // 7200) + 1) * 7200 + offset
    next_spawn = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(seconds=next_spawn_seconds)
    return next_spawn

def get_next_mini_time():
    now = datetime.datetime.now()
    if now.minute < 30:
        next_spawn = now.replace(minute=30, second=0, microsecond=0)
    else:
        next_spawn = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    return next_spawn

# Command to check remaining time using the prefix "!"
@bot.command(name="timer")
async def timer(ctx, spawn_type: str = None):
    if spawn_type is None or spawn_type.lower() not in ['mvp', 'mini']:
        await ctx.send("Commandnya salah kocak minimal tambahin: `mvp` atau `mini`.\nExample: `!timer mvp`")
        return

    now = datetime.datetime.now()
    if spawn_type.lower() == 'mvp':
        next_time = get_next_mvp_time()
    else:
        next_time = get_next_mini_time()

    remaining = next_time - now
    total_seconds = int(remaining.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.send(
        f"Time remaining for **{spawn_type.upper()}** spawn: {hours} hours, {minutes} minutes, {seconds} seconds."
    )

bot.run(TOKEN)
