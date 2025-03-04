from pyrogram import filters
from pyrogram import __version__
from bot import Bot
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
import random  # Import random to select a random photo

# Function to redeploy the bot
def redeploy_bot():
    os.system("git pull")
    os.execv(sys.executable, ['python3'] + sys.argv)

# Global variable to store the message and chat ID for saving state
saving_message = None

# List of photo URLs
photos = [
    "https://litter.catbox.moe/21bhag.jpg",
    "https://litter.catbox.moe/8ngis1.jpg",
    # Add more photo URLs as needed
]

@Bot.on_message(filters.command("help"))
async def help_command(client, message):
    # Define the inline keyboard buttons
    buttons = [
        [
            InlineKeyboardButton("Get Link", callback_data="get_link"),
            InlineKeyboardButton("Broadcast", callback_data="broadcast"),
            InlineKeyboardButton("Users", callback_data="users")
        ],
        [
            InlineKeyboardButton("FSub", callback_data="fsub"),
            InlineKeyboardButton("Dev", callback_data="dev")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ]

    # Select a random photo from the list
    random_photo = random.choice(photos)

    # Send the help message with a random photo and inline buttons
    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_photo,
        caption="Here are the available commands:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    global saving_message
    data = query.data
    
    if data == "about":
        await query.message.edit_text(
            text=f"<b>🤖 My Name :</b> <a href='https://t.me/Anime_file_share669bot'>Grimmjow</a> \n<b>📝 Language :</b> <a href='https://python.org'>Python 3</a> \n<b>📚 Library :</b> <a href='https://github.com/pyrogram/pyrogram'>Pyrogram</a>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🔐 Close", callback_data="close")]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
        
        close_message = await client.send_message(
            chat_id=query.message.chat.id,
            text=f"close by {query.from_user.mention}"
        )
        await sleep(10)
        await close_message.delete()
    
    elif data in ["get_link", "broadcast", "users", "fsub", "dev"]:
        await query.answer("Under development", show_alert=True)
    
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
            f"Force Sub Channel 1 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel and have given it admin rights.",
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
            f"Force Sub Channel 2 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel and have given it admin rights.",
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
            f"Force Sub Channel 3 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel and have given it admin rights.",
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
            f"Force Sub Channel 4 successfully updated to {new_channel_id} \n\nPlease restart the bot to see the changes in action! /restart \n\nNote: Make sure you have added the bot to the new channel and have given it admin rights.",
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
