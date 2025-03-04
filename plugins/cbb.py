from pyrogram import filters
from pyrogram import __version__
from common import Bot  # Import Bot from common module
from config import OWNER_ID, SUDO_USERS, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
from database.db_handler import set_force_sub_channel, get_force_sub_channel
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import os
import signal
import sys
from database.db_handler import set_auto_delete_time  # Import the function to set auto delete time
from database.db_handler import add_admin, remove_admin, get_admins
from utils import update_saved_button_state  # Import the function
from asyncio import sleep  # Import sleep for the auto-delete functionality

# Function to redeploy the bot
def redeploy_bot():
    os.system("git pull")
    os.execv(sys.executable, ['python3'] + sys.argv)

# Global variable to store the message and chat ID for saving state
saving_message = None

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    global saving_message
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text = f"<b>🤖 My Name :</b> <a href='https://t.me/Anime_file_share669bot'>Grimmjow</a> \n<b>📝 Language :</b> <a href='https://python.org'>Python 3</a> \n<b>📚 Library :</b> <a href='https://pyrogram.org'>Pyrogram {__version__}</a> \n<b>🚀 Server :</b> <a href='https://heroku.com'>Heroku</a> \n<b>📢 Channel :</b> <a href='https://t.me/Madflix_Bots'>Madflix Botz</a> \n<b>👨‍💻 Developer :</b> <a href='tg://user?id={OWNER_ID}'>Jishu Developer</a>",
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
        
        # Send the close message and delete it after 10 seconds
        close_message = await client.send_message(
            chat_id=query.message.chat.id,
            text=f"close by {query.from_user.mention}"
        )
        await sleep(10)
        await close_message.delete()
        
    elif data == "save":
        saving_message = query.message
        await query.message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton("💾 Saving...", callback_data="saving")]])
        )
        os.kill(os.getpid(), signal.SIGINT)
        redeploy_bot()
    elif data == "saving":
        user_id = query.from_user.id
        if user_id == OWNER_ID or user_id in SUDO_USERS:
            await query.message.edit_reply_markup(
                InlineKeyboardMarkup([[InlineKeyboardButton("✅ Saved", callback_data="saved")]])
            )
        await query.answer()  # Answer the callback query to stop the loading animation

# Add the rest of your functions here

@Bot.on_message(filters.command("add_fsub1") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub1(client, message):
    try:
        command, new_channel_id = message.text.split()
        new_channel_id = int(new_channel_id)
        set_force_sub_channel(1, new_channel_id)

        # Log the new channel ID
        log_channel_id = -1002121888464
        await client.send_message(log_channel_id, f"Force Sub Channel 1 updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart")

        await message.reply(
            f"Force Sub Channel 1 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel as an admin with the invite via link permission enabled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )

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

        await message.reply(
            f"Force Sub Channel 2 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel as an admin with the invite via link permission enabled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )

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

        await message.reply(
            f"Force Sub Channel 3 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel as an admin with the invite via link permission enabled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )

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

        await message.reply(
            f"Force Sub Channel 4 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel as an admin with the invite via link permission enabled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )

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

@Bot.on_message(filters.command("setautodel") & filters.user([OWNER_ID] + SUDO_USERS))
async def set_auto_delete_time_command(client, message):
    try:
        command, new_auto_delete_time = message.text.split()
        new_auto_delete_time = int(new_auto_delete_time)
        
        set_auto_delete_time(new_auto_delete_time)  # Update the auto delete time in the database
        
        # Log the new auto delete time
        log_channel_id = -1002121888464
        await client.send_message(log_channel_id, f"Auto delete time updated to {new_auto_delete_time} seconds \n\nPlease restart the bot to see the changes in action! /restart")
        
        await message.reply(
            f"Auto delete time successfully updated to {new_auto_delete_time} seconds \n\nPlease restart the bot to see the changes in action! /restart",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )
        
    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

@Bot.on_message(filters.command("addadmin") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_admin_command(client, message):
    try:
        command, user_identifier = message.text.split()
        if user_identifier.isdigit():
            user_id = int(user_identifier)
        else:
            user = await client.get_users(user_identifier)
            user_id = user.id

        add_admin(user_id)
        await refresh_admins_list()
        await message.reply(
            f"Admin {user_identifier} added successfully.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )
    except Exception as e:
        await message.reply(f"Error: {e}")

@Bot.on_message(filters.command("rmadmin") & filters.user([OWNER_ID] + SUDO_USERS))
async def remove_admin_command(client, message):
    try:
        command, user_identifier = message.text.split()
        if user_identifier.isdigit():
            user_id = int(user_identifier)
        else:
            user = await client.get_users(user_identifier)
            user_id = user.id

        admins = get_admins()
        if user_id not in admins:
            await message.reply(f"Admin {user_identifier} not found.")
            return

        remove_admin(user_id)
        await refresh_admins_list()
        await message.reply(
            f"Admin {user_identifier} removed successfully.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💾 Save", callback_data="save")]])  # Added Save button here
        )
    except Exception as e:
        await message.reply(f"Error: {e}")

async def refresh_admins_list():
    global ADMINS
    ADMINS = get_admins()

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
