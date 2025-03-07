from pyrogram import filters
from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, SUDO_USERS, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
from database.db_handler import set_force_sub_channel, get_force_sub_channel
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db_handler import set_auto_delete_time  # Import the function to set auto delete time
from database.db_handler import add_admin, remove_admin, get_admins
from utils import update_saved_button_state  # Import the function
from asyncio import sleep  # Import sleep for the auto-delete functionality
import random  # Import random to select a random photo

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
            text=f"<b>🤖 My Name :</b> <a href='https://t.me/Anime_file_share669bot'>Grimmjow</a> \n<b>📝 Language :</b> <a href='https://python.org'>Python 3</a> \n<b>📚 Library :</b> <a hr[...]",
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
            text=f"Closed by {query.from_user.mention}"
        )
        await sleep(10)
        await close_message.delete()
    
    elif data == "cancel":
        await query.message.edit_text(f"Operation cancelled by {query.from_user.mention}")
    
    elif data.startswith("confirm_save_fsub1_"):
        new_channel_id = int(data.split("_")[-1])
        set_force_sub_channel(1, new_channel_id)
        await query.message.edit_text(f"Force Sub Channel 1 successfully updated to {new_channel_id}. Saved by {query.from_user.mention}")
    
    elif data.startswith("confirm_save_fsub2_"):
        new_channel_id = int(data.split("_")[-1])
        set_force_sub_channel(2, new_channel_id)
        await query.message.edit_text(f"Force Sub Channel 2 successfully updated to {new_channel_id}. Saved by {query.from_user.mention}")
    
    elif data.startswith("confirm_save_fsub3_"):
        new_channel_id = int(data.split("_")[-1])
        set_force_sub_channel(3, new_channel_id)
        await query.message.edit_text(f"Force Sub Channel 3 successfully updated to {new_channel_id}. Saved by {query.from_user.mention}")
    
    elif data.startswith("confirm_save_fsub4_"):
        new_channel_id = int(data.split("_")[-1])
        set_force_sub_channel(4, new_channel_id)
        await query.message.edit_text(f"Force Sub Channel 4 successfully updated to {new_channel_id}. Saved by {query.from_user.mention}")
    
    elif data.startswith("confirm_save_admin_"):
        user_id = int(data.split("_")[-1])
        add_admin(user_id)
        await refresh_admins_list()
        await query.message.edit_text(f"Admin {user_id} added successfully. Saved by {query.from_user.mention}")
    
    elif data.startswith("confirm_remove_admin_"):
        user_id = int(data.split("_")[-1])
        admins = get_admins()
        if user_id in admins:
            remove_admin(user_id)
            await refresh_admins_list()
            await query.message.edit_text(f"Admin {user_id} removed successfully. Saved by {query.from_user.mention}")
        else:
            await query.message.edit_text(f"Admin {user_id} not found")

@Bot.on_message(filters.command("add_fsub1") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub1(client, message):
    try:
        command, new_channel_id = message.text.split()
        new_channel_id = int(new_channel_id)

        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to update Force Sub Channel 1 to {new_channel_id}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_save_fsub1_{new_channel_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
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

        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to update Force Sub Channel 2 to {new_channel_id}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_save_fsub2_{new_channel_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
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

        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to update Force Sub Channel 3 to {new_channel_id}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_save_fsub3_{new_channel_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
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

        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to update Force Sub Channel 4 to {new_channel_id}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_save_fsub4_{new_channel_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )

    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

@Bot.on_message(filters.command("setautodel") & filters.user([OWNER_ID] + SUDO_USERS))
async def set_auto_delete_time_command(client, message):
    try:
        command, new_auto_delete_time = message.text.split()
        new_auto_delete_time = int(new_auto_delete_time)
        
        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to update the auto delete time to {new_auto_delete_time} seconds?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_save_autodel_{new_auto_delete_time}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )

    except ValueError as e:
        await message.reply(f"ValueError: {e}")
    except Exception as e:
        await message.reply(f"Exception: {e}")

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    global saving_message
    data = query.data

    if data.startswith("confirm_save_autodel_"):
        new_auto_delete_time = int(data.split("_")[-1])
        set_auto_delete_time(new_auto_delete_time)
        await query.message.edit_text(f"Auto delete time updated to {new_auto_delete_time} seconds. Saved by {query.from_user.mention}")
    
    elif data == "cancel":
        await query.message.edit_text(f"Operation cancelled by {query.from_user.mention}")

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

@Bot.on_message(filters.command("addadmin") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_admin_command(client, message):
    try:
        command, user_identifier = message.text.split()
        if user_identifier.isdigit():
            user_id = int(user_identifier)
        else:
            user = await client.get_users(user_identifier)
            user_id = user.id

        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to add admin {user_identifier}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_save_admin_{user_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
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

        # Send confirmation message with buttons
        await message.reply(
            f"Are you sure you want to remove admin {user_identifier}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm Save", callback_data=f"confirm_remove_admin_{user_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
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
