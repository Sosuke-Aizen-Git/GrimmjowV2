from pyrogram import filters, __version__
from bot import Bot
import pymongo
from config import OWNER_ID, SUDO_USERS, DB_URL, DB_NAME, PHOTOS
from database.db_handler import (
    set_force_sub_channel, get_force_sub_channel, set_auto_delete_time, 
    add_admin, remove_admin, get_admins
)
from plugins.refresh import refresh_database, refresh_force_sub_channels, cache_invite_links, refresh_command, refresh_auto_delete_time, refresh_admins
import random
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asyncio import sleep


@Bot.on_message(filters.command("help"))
async def help_command(client, message):
    await message.react("👍")
    buttons = [
        [InlineKeyboardButton("🔗 Get Link", callback_data="get_link"),
         InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
         InlineKeyboardButton("👥 Users", callback_data="users")],
        [InlineKeyboardButton("🔒 FSub", callback_data="fsub"),
         InlineKeyboardButton("👨‍💻 Dev", callback_data="dev")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]

    await client.send_photo(
        chat_id=message.chat.id,
        photo=random.choice(PHOTOS),
        caption="✨ **Here are the available commands:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "about":
        await query.message.edit_text(
            text=f"🤖 **Bot Name:** [Red Hood](https://t.me/Anime_file_share669bot)\n"
                 f"📝 **Language:** [Python 3](https://python.org)\n"
                 f"📚 **Library:** [Pyrogram {__version__}](https://pyrogram.org)",
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
            text=f"✅ **Closed by {query.from_user.mention}**"
        )
        await sleep(5)
        await close_message.delete()

    elif data == "cancel":
        await query.message.edit_text(f"⚠️ **Operation cancelled by {query.from_user.mention}**")

    elif data.startswith("confirm_save_fsub_"):
        if query.from_user.id in SUDO_USERS:
            await refresh_database()
            await refresh_force_sub_channels()
            channel_index = int(data.split("_")[-2])
            new_channel_id = int(data.split("_")[-1])
            set_force_sub_channel(channel_index, new_channel_id)
            await query.message.edit_text(f"✅ **Force Subscription updated!**\n📢 Channel {channel_index} ➝ `{new_channel_id}`\n🔄 Database refreshed.")

    elif data.startswith("confirm_save_admin_"):
        if query.from_user.id in SUDO_USERS:
            await refresh_database()
            await refresh_admins()
            user_id = int(data.split("_")[-1])
            add_admin(user_id)
            await query.message.edit_text(f"✅ **Admin `{user_id}` added successfully!**")

    elif data.startswith("confirm_remove_admin_"):
        if query.from_user.id in SUDO_USERS:
            await refresh_database()
            await refresh_admins()
            user_id = int(data.split("_")[-1])
            admins = get_admins()
            if user_id in admins:
                remove_admin(user_id)
                await query.message.edit_text(f"✅ **Admin `{user_id}` removed successfully!**")
            else:
                await query.message.edit_text(f"⚠️ **Admin `{user_id}` not found!**")

    elif data.startswith("confirm_save_autodel_"):
        if query.from_user.id in SUDO_USERS:
            await refresh_database()
            await refresh_auto_delete_time()
            new_auto_delete_time = int(data.split("_")[-1])
            set_auto_delete_time(new_auto_delete_time)
            await query.message.edit_text(f"✅ **Auto-delete time updated to {new_auto_delete_time} seconds!**\n🔄 Database refreshed.")

    elif data == "get_link":
        await query.message.edit_text(
            text="📌 **Link Generation Commands:**\n"
                 "🔹 `/genlink` - Generate a single file/video link (Admins only)\n"
                 "🔹 `/batch` - Generate multiple file/video links (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "users":
        await query.message.edit_text(
            text="👥 **User Management:**\n"
                 "🔹 `/users` - View total users (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "fsub":
        await query.message.edit_text(
            text="🔒 **Force Subscription:**\n"
                 "🔹 `/add_fsub {Index} {Channel ID}` - Set a force sub channel (Sudo only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "broadcast":
        await query.message.edit_text(
            text="📢 **Broadcast Commands:**\n"
                 "🔹 `/broadcast` - Send a message to all users (Admins only)\n"
                 "🔹 `/fpbroadcast` - Send a forwardable broadcast (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "dev":
        await query.message.edit_text(
            text="👨‍💻 **Developer Commands:**\n"
                 "🔹 `/refresh` - Refresh the database (Owner only)\n"
                 "🔹 `/restart` - Restart the bot (Owner only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "back_to_help":
        buttons = [
            [InlineKeyboardButton("🔗 Get Link", callback_data="get_link"),
             InlineKeyboardButton("📢 Broadcast", callback_data="broadcast"),
             InlineKeyboardButton("👥 Users", callback_data="users")],
            [InlineKeyboardButton("🔒 FSub", callback_data="fsub"),
             InlineKeyboardButton("👨‍💻 Dev", callback_data="dev")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        await query.message.edit_text(
            text="✨ **Here are the available commands:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
