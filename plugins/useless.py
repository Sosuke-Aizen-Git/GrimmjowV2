from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from datetime import datetime
from helper_func import get_readable_time
from config import ADMINS
from database.database import full_userbase
import time

async def get_ping(bot):
    start = time.time()
    await bot.get_me()
    end = time.time()
    ping = (end - start) * 1000  # Convert to milliseconds
    return round(ping, 3)  # Round to 3 decimal places

@Bot.on_message(filters.command('stats') & filters.user(ADMINS))
async def stats(bot: Bot, message: Message):
    now = datetime.now()
    delta = now - bot.uptime
    time = get_readable_time(delta.seconds)
    ping = await get_ping(bot)
    total_users_count = len(await full_userbase())

    status_message = (
        "```Bot Status\n"
        f"⏳ Bot Uptime: {time}\n"
        f"⚡️ Current Ping: {ping} ms\n"
        f"👤 Total Users: {total_users_count}```"
    )
    await message.reply(status_message)

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
