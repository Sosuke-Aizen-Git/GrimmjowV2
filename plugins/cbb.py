from pyrogram import filters, __version__
from bot import Bot
import pymongo
from config import OWNER_ID, SUDO_USERS, DB_URL, DB_NAME
from database.db_handler import (
    set_force_sub_channel, get_force_sub_channel, set_auto_delete_time, 
    add_admin, remove_admin, get_admins
)
from database.db_handler import get_force_sub_channel, refresh_db_handler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asyncio import sleep
from plugins.refresh import refresh_database, refresh_force_sub_channels, cache_invite_links, refresh_command
import random
    
# Photo URLs
photos = [
    "https://litter.catbox.moe/21bhag.jpg",
    "https://litter.catbox.moe/8ngis1.jpg",
]

@Bot.on_message(filters.command("help"))
async def help_command(client, message):
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

    await client.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(photos),
        caption="Here are the available commands:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "about":
        await query.message.edit_text(
            text=f"<b>🤖 Bot Name:</b> <a href='https://t.me/Anime_file_share669bot'>Grimmjow</a>\n"
                 f"<b>📝 Language:</b> <a href='https://python.org'>Python 3</a>\n"
                 f"<b>📚 Library:</b> <a href='https://pyrogram.org'>Pyrogram {__version__}</a>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔐 Close", callback_data="close")]])
        )

    elif data == "close":
        try:
            await query.message.delete()
            if query.message.reply_to_message:
                await query.message.reply_to_message.delete()
        except:
            pass

        close_message = await client.send_message(
            chat_id=query.message.chat.id,
            text=f"Closed by {query.from_user.mention}"
        )
        await sleep(5)
        await close_message.delete()

    elif data == "cancel":
        await query.message.edit_text(f"Operation cancelled by {query.from_user.mention}")

    elif data.startswith("confirm_save_fsub_"):
        await refresh_database()
        await refresh_db_handler()
        await refresh_force_sub_channels()
        channel_index = int(data.split("_")[-2])
        new_channel_id = int(data.split("_")[-1])
        set_force_sub_channel(channel_index, new_channel_id)
        await query.message.edit_text(f"Force Sub Channel {channel_index} updated to {new_channel_id}. Database refreshed. Saved by {query.from_user.mention}")
    elif data.startswith("confirm_save_admin_"):
        await refresh_database()
        await refresh_db_handler()
        await refresh_force_sub_channels()
        user_id = int(data.split("_")[-1])
        add_admin(user_id)
        await query.message.edit_text(f"Admin {user_id} added successfully. Saved by {query.from_user.mention}")

    elif data.startswith("confirm_remove_admin_"):
        await refresh_database()
        await refresh_db_handler()
        await refresh_force_sub_channels()
        user_id = int(data.split("_")[-1])
        admins = get_admins()
        if user_id in admins:
            remove_admin(user_id)
            await query.message.edit_text(f"Admin {user_id} removed successfully. Saved by {query.from_user.mention}")
        else:
            await query.message.edit_text(f"Admin {user_id} not found")

    elif data.startswith("confirm_save_autodel_"):
        await refresh_database()
        await refresh_db_handler()
        await refresh_force_sub_channels()
        new_auto_delete_time = int(data.split("_")[-1])
        set_auto_delete_time(new_auto_delete_time)
        await query.message.edit_text(f"Auto delete time updated to {new_auto_delete_time} seconds and Database refreshed. Saved by {query.from_user.mention}")

    # Implementing feature buttons
    elif data == "get_link":
        await query.message.edit_text(
            text="/genlink - Generate a single Video/File link (Admins only)\n"
                 "/batch - Generate multiple Videos/Files links (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "users":
        await query.message.edit_text(
            text="/users - Check total users (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "fsub":
        await query.message.edit_text(
            text="/add_fsub <Index> <Channel ID> - Set a force sub channel (Sudo only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "broadcast":
        await query.message.edit_text(
            text="/broadcast - Send a broadcast message (Admins only)\n"
                 "/fpbroadcast - Send a forwardable broadcast (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "dev":
        await query.message.edit_text(
            text="/refresh - Refresh the database (Owner only)\n"
                 "/restart - Restart the bot (Owner only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "back_to_help":
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
        await query.message.edit_caption(
            caption="Here are the available commands:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@Bot.on_message(filters.command("add_fsub") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_fsub(client, message):
    try:
        _, index, new_channel_id = message.text.split()
        index, new_channel_id = int(index), int(new_channel_id)

        await message.reply(
            f"Are you sure you want to update Force Sub Channel {index} to {new_channel_id}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_save_fsub_{index}_{new_channel_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )
    except Exception as e:
        await message.reply(f"Error: {e}")

@Bot.on_message(filters.command("setautodel") & filters.user([OWNER_ID] + SUDO_USERS))
async def set_auto_delete_time_command(client, message):
    try:
        _, new_auto_delete_time = message.text.split()
        new_auto_delete_time = int(new_auto_delete_time)

        await message.reply(
            f"Set auto delete time to {new_auto_delete_time} seconds?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_save_autodel_{new_auto_delete_time}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )
    except Exception as e:
        await message.reply(f"Error: {e}")

@Bot.on_message(filters.command("addadmin") & filters.user([OWNER_ID] + SUDO_USERS))
async def add_admin_command(client, message):
    try:
        _, user_identifier = message.text.split()
        user_id = int(user_identifier) if user_identifier.isdigit() else (await client.get_users(user_identifier)).id

        await message.reply(
            f"Add admin {user_identifier}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_save_admin_{user_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )
    except Exception as e:
        await message.reply(f"Error: {e}")

@Bot.on_message(filters.command("rmadmin") & filters.user([OWNER_ID] + SUDO_USERS))
async def remove_admin_command(client, message):
    try:
        _, user_identifier = message.text.split()
        if user_identifier.isdigit():
            user_id = int(user_identifier)
        else:
            user = await client.get_users(user_identifier)
            user_id = user.id

        await message.reply(
            f"Are you sure you want to remove admin {user_identifier}?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_remove_admin_{user_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ])
        )

    except Exception as e:
        await message.reply(f"Error: {e}")

async def check_force_sub(client, user_id):
    channels = [get_force_sub_channel(i) for i in range(1, 5)]
    for channel in channels:
        if channel:
            try:
                member = await client.get_chat_member(channel, user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    return False
            except:
                return False
    return True

# Define the refresh_db_handler function
async def refresh_db_handler():
    # Your code to refresh the database
    pass
