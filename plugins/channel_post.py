import asyncio
import os
import signal
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, OWNER_ID, SUDO_USERS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from database.db_handler import get_admins
from helper_func import encode
import sys

# Function to redeploy the bot
def redeploy_bot():
    os.system("git pull")
    os.execv(sys.executable, ['python3'] + sys.argv)

@Bot.on_message(filters.command("restart") & filters.user([OWNER_ID] + SUDO_USERS))
async def restart_bot(client: Client, message: Message):
    await message.reply_text("Bot is restarting...")
    os.kill(os.getpid(), signal.SIGINT)
    redeploy_bot()

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats', 'fsubs', 'admins', 'fpbroadcast', 'id', 'add_fsub1', 'add_fsub2', 'add_fsub3', 'add_fsub4', 'refresh', 'restart', 'autodel', 'setautodel', 'addadmin', 'rmadmin', 'logs', 'help']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something Went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])

    await reply_text.edit(f"<b>Here Is Your Link</b>\n\n{link}", reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)

@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]])
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
