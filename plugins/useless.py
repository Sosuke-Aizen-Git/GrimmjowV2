import random
from plugins.start import photos
import time
from bot import Bot
from pyrogram.types import Message
from pyrogram import filters
from datetime import datetime
from helper_func import get_readable_time
from config import ADMINS, SUDO_USERS
from database.database import full_userbase
from database.db_handler import get_admins

# List of images (local file paths or URLs)

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

        now = datetime.now()
        delta = now - bot.uptime
        time = get_readable_time(delta.seconds)
        ping = await get_ping(bot)
        total_users_count = len(await full_userbase())

        status_message = (
            f"<pre language='@RedHoodXbot Bot Status:'>"
            f"⏳ Bot Uptime: {time}\n"
            f"⚡ Current Ping: {ping} ms\n"
            f"👤 Total Users: {total_users_count}"
            f"</pre>"
        )

        # Select a random image from the list
        random_image = random.choice(photos)

        # Send the image first
        await message.reply_photo(photo=random_image, caption=status_message)

        # Use `bot.send_message()` to apply the effect
        await bot.send_message(
    chat_id=message.chat.id,
    text="✨ Status Updated!",
    **{"message_effect_id": 5046509860389126442}  # Pass as a keyword argument
)

        await sticker.delete()
    else:
        await message.reply_text("You are not an authorized user!")
