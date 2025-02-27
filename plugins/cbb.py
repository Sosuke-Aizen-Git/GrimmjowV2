from pyrogram import filters
from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, SUDO_USERS, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
from database.db_handler import set_force_sub_channel, get_force_sub_channel
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>🤖 My Name :</b> <a href='https://t.me/Anime_file_share669bot'>Grimmjow</a> \n<b>📝 Language :</b> <a href='https://python.org'>Python 3</a> \n<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram</a> v{__version__}",
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔐 Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

@Bot.on_message(filters.command("add_fsub1") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub1(client, message):
    try:
        command, new_channel_id = message.text.split()
        new_channel_id = int(new_channel_id)
        set_force_sub_channel(1, new_channel_id)

        # Log the new channel ID
        log_channel_id = -1002121888464
        await client.send_message(log_channel_id, f"Force Sub Channel 1 updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart")

        await message.reply(f"Force Sub Channel 1 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot as admin with invite users permission in your force sub channel otherwise force sub will not work properly!.")

    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

@Bot.on_message(filters.command("add_fsub2") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub2(client, message):
    try:
        command, new_channel_id = message.text.split()
        new_channel_id = int(new_channel_id)
        set_force_sub_channel(2, new_channel_id)

        # Log the new channel ID
        log_channel_id = -1002121888464
        await client.send_message(log_channel_id, f"Force Sub Channel 2 updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart")

        await message.reply(f"Force Sub Channel 2 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot as admin with invite users permission in your force sub channel otherwise force sub will not work properly!.")

    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

@Bot.on_message(filters.command("add_fsub3") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub3(client, message):
    try:
        command, new_channel_id = message.text.split()
        new_channel_id = int(new_channel_id)
        set_force_sub_channel(3, new_channel_id)

        # Log the new channel ID
        log_channel_id = -1002121888464
        await client.send_message(log_channel_id, f"Force Sub Channel 3 updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart")

        await message.reply(f"Force Sub Channel 3 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot as admin with invite users permission in your force sub channel otherwise force sub will not work properly!.")

    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

@Bot.on_message(filters.command("add_fsub4") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub4(client, message):
    try:
        command, new_channel_id = message.text.split()
        new_channel_id = int(new_channel_id)
        set_force_sub_channel(4, new_channel_id)

        # Log the new channel ID
        log_channel_id = -1002121888464
        await client.send_message(log_channel_id, f"Force Sub Channel 4 updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart")

        await message.reply(f"Force Sub Channel 4 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot as admin with invite users permission in your force sub channel otherwise force sub will not work properly!.")

    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

async def check_force_sub(client, user_id):
    # Dynamically fetch the updated force sub channels
    channels = [get_force_sub_channel(1), get_force_sub_channel(2), get_force_sub_channel(3), get_force_sub_channel(4)]
    for channel in channels:
        if channel:
            try:
                member = await client.get_chat_member(channel, user_id)
                if member and member.status in ["member", "administrator", "creator"]:
                    continue
                else:
                    return False
            except:
                return False
    return True

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
