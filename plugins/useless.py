import random
import time
import psutil
import shutil
from datetime import datetime
from config import PHOTOS
from bot import Bot
from pyrogram import filters
from pyrogram.types import Message
from helper_func import get_readable_time
from config import ADMINS, SUDO_USERS
from database.database import full_userbase
from database.db_handler import get_admins

async def get_ping(bot):
    start = time.time()
    await bot.get_me()
    end = time.time()
    ping = (end - start) * 1000  # Convert to milliseconds
    return round(ping, 3)  # Round to 3 decimal places

@Bot.on_message(filters.command('stats'))
async def stats(bot: Bot, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        sticker = await message.reply_sticker("CAACAgUAAxkBAAEG8_xnzbAQQOfHqMQrzWcOHBvU78EiRgAC_hMAAqiR-FZkMEjJt_CizDYE")
        
        # Bot Uptime Calculation
        now = datetime.now()
        delta = now - bot.uptime
        uptime = get_readable_time(delta.seconds)
        
        # Get bot ping
        ping = await get_ping(bot)

        # Get total users count
        total_users_count = len(await full_userbase())

        # System Stats
        cpu_usage = psutil.cpu_percent()
        cpu_freq = psutil.cpu_freq().current

        ram = psutil.virtual_memory()
        total_ram = round(ram.total / (1024 ** 3), 2)
        used_ram = round(ram.used / (1024 ** 3), 2)
        free_ram = round(ram.available / (1024 ** 3), 2)
        ram_usage = ram.percent

        disk = shutil.disk_usage("/")
        total_rom = round(disk.total / (1024 ** 3), 2)
        used_rom = round(disk.used / (1024 ** 3), 2)
        free_rom = round(disk.free / (1024 ** 3), 2)
        rom_usage = round((used_rom / total_rom) * 100, 2)

        # Status message
        status_message = f"""
**📊 BOT STATISTICS:**
**➤ Uptime:** `{uptime}`
**➤ Ping:** `{ping} ms`
**➤ Total Users:** `{total_users_count}`

**📌 CPU Usage:** `{cpu_usage}%`
• **CPU Frequency:** `{cpu_freq} MHz`

**📌 RAM Usage:** `{ram_usage}%`
• **Total RAM:** `{total_ram} GB`
• **Free RAM:** `{free_ram} GB`
• **Used RAM:** `{used_ram} GB`

**📌 ROM Usage:** `{rom_usage}%`
• **Total ROM:** `{total_rom} GB`
• **Free ROM:** `{free_rom} GB`
• **Used ROM:** `{used_rom} GB`
"""

        # Select a random image from the list
        random_image = random.choice(PHOTOS)

        await message.reply_photo(
            photo=random_image,
            caption=status_message
        )
        await sticker.delete()
    else:
        await message.reply_text("You are not an authorized user!")
