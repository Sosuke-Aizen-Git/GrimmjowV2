import random
import time
import psutil
import shutil
from datetime import datetime
from config import PHOTOS
from bot import BOT_START_TIME
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from helper_func import get_readable_time  # Using your existing function
from config import ADMINS, SUDO_USERS
from database.database import full_userbase
from database.db_handler import get_admins

# Dictionary to track cooldown for users
cooldown_tracker = {}

# Function to generate progress bars
def progress_bar(percentage, size=10):
    filled = round(percentage / 10)  # Scale to fit the bar size
    bar = "█" * filled + "░" * (size - filled)  # Create bar with filled & empty blocks
    return f"<code>[{bar}] {percentage:.1f}%</code>"

async def get_ping(bot):
    start = time.time()
    await bot.get_me()
    end = time.time()
    ping = (end - start) * 1000  # Convert to milliseconds
    return round(ping, 2)  # Round to 2 decimal places

from bot import BOT_START_TIME  # Import global start time

async def get_bot_stats(bot):
    # Corrected Uptime Calculation
    now = datetime.now()
    delta = now - BOT_START_TIME  # Use global start time
    uptime = get_readable_time(int(delta.total_seconds()))  # Convert to int

    # Keep the rest of the function unchanged...
    
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

    # Status message with progress bars
    status_message = f"""
<blockquote>📊 <b>BOT STATISTICS</b></blockquote>
<b>➤ Uptime:</b> <code>{uptime}</code>
<b>➤ Ping:</b> <code>{ping} ms</code>
<b>➤ Total Users:</b> <code>{total_users_count}</code>

<b>📌 CPU Usage:</b> <code>{cpu_usage}%</code>
{progress_bar(cpu_usage)}
• <b>CPU Frequency:</b> <code>{cpu_freq} MHz</code>

<b>📌 RAM Usage:</b> <code>{ram_usage}%</code>
{progress_bar(ram_usage)}
• <b>Total RAM:</b> <code>{total_ram} GB</code>
• <b>Free RAM:</b> <code>{free_ram} GB</code>
• <b>Used RAM:</b> <code>{used_ram} GB</code>

<b>📌 ROM Usage:</b> <code>{rom_usage}%</code>
{progress_bar(rom_usage)}
• <b>Total ROM:</b> <code>{total_rom} GB</code>
• <b>Free ROM:</b> <code>{free_rom} GB</code>
• <b>Used ROM:</b> <code>{used_rom} GB</code>
"""

    return status_message

@Bot.on_message(filters.command('stats'))
async def stats(bot: Bot, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        sticker = await message.reply_sticker("CAACAgUAAxkBAAEG8_xnzbAQQOfHqMQrzWcOHBvU78EiRgAC_hMAAqiR-FZkMEjJt_CizDYE")
        
        # Generate bot stats
        status_message = await get_bot_stats(bot)

        # Select a random image from the list
        random_image = random.choice(PHOTOS)

        # Inline buttons for refreshing and closing stats
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="refresh_stats")],
            [InlineKeyboardButton("❌ Close", callback_data="close_stats")]
        ])

        sent_message = await message.reply_photo(
            photo=random_image,
            caption=status_message,
            reply_markup=keyboard
        )
        await sticker.delete()
    else:
        await message.reply_text("<b>You are not an authorized user!</b>")

@Bot.on_callback_query(filters.regex("refresh_stats"))
async def refresh_stats(bot: Client, query: CallbackQuery):
    user_id = query.from_user.id

    # Check if user is authorized
    if user_id not in get_admins() + SUDO_USERS:
        await query.answer("❌ You can't use this!", show_alert=True)
        return

    current_time = time.time()

    # Check if user is in cooldown
    if user_id in cooldown_tracker:
        last_used = cooldown_tracker[user_id]
        time_diff = current_time - last_used
        if time_diff < 5:  # 5-second cooldown
            await query.answer(f"⏳ Please wait {5 - int(time_diff)}s before refreshing again!", show_alert=True)
            return

    # Update cooldown tracker
    cooldown_tracker[user_id] = current_time

    # Update the statistics
    updated_stats = await get_bot_stats(bot)

    # Edit the message with new stats
    await query.message.edit_caption(
        caption=updated_stats,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="refresh_stats")],
            [InlineKeyboardButton("❌ Close", callback_data="close_stats")]
        ])
    )
    await query.answer("✅ Stats updated!")

@Bot.on_callback_query(filters.regex("close_stats"))
async def close_stats(bot: Client, query: CallbackQuery):
    user_id = query.from_user.id

    # Check if user is authorized
    if user_id not in get_admins() + SUDO_USERS:
        await query.answer("❌ You can't use this!", show_alert=True)
        return

    # Delete the stats message
    await query.message.delete()
    await query.answer("🗑️ Stats message deleted!")
