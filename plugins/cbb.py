from pyrogram import filters, __version__
from bot import Bot
from config import OWNER_ID, SUDO_USERS
from database.db_handler import (
    set_force_sub_channel, get_force_sub_channel, set_auto_delete_time, 
    add_admin, remove_admin, get_admins
)
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from asyncio import sleep
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
        channel_index = int(data.split("_")[-2])
        new_channel_id = int(data.split("_")[-1])
        set_force_sub_channel(channel_index, new_channel_id)
        await query.message.edit_text(f"Force Sub Channel {channel_index} updated to {new_channel_id}. Saved by {query.from_user.mention}")

    elif data.startswith("confirm_save_admin_"):
        user_id = int(data.split("_")[-1])
        add_admin(user_id)
        await query.message.edit_text(f"Admin {user_id} added successfully. Saved by {query.from_user.mention}")

    elif data.startswith("confirm_remove_admin_"):
        user_id = int(data.split("_")[-1])
        admins = get_admins()
        if user_id in admins:
            remove_admin(user_id)
            await query.message.edit_text(f"Admin {user_id} removed successfully. Saved by {query.from_user.mention}")
        else:
            await query.message.edit_text(f"Admin {user_id} not found")

    elif data.startswith("confirm_save_autodel_"):
        new_auto_delete_time = int(data.split("_")[-1])
        set_auto_delete_time(new_auto_delete_time)
        await query.message.edit_text(f"Auto delete time updated to {new_auto_delete_time} seconds. Saved by {query.from_user.mention}")

    # Handling new buttons
    elif data == "get_link":
        await query.message.edit_text(
            text="/genlink - To generate a single Video/file link. (Admins only)\n"
                 "/batch - To generate multiple Videos/files links. (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "users":
        await query.message.edit_text(
            text="/users - To check total users (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "fsub":
        await query.message.edit_text(
            text="/add_fsub1 <Channel ID> - To set the first force sub channel (Sudo only)\n"
                 "/add_fsub2 <Channel ID> - To set the second force sub channel (Sudo only)\n"
                 "/add_fsub3 <Channel ID> - To set the third force sub channel (Sudo only)\n"
                 "/add_fsub4 <Channel ID> - To set the fourth force sub channel (Sudo only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "broadcast":
        await query.message.edit_text(
            text="/broadcast - To broadcast to users (Admins only)\n"
                 "/fpbroadcast - To broadcast with sender tag (Admins only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "dev":
        await query.message.edit_text(
            text="/refresh - To refresh the database (Owner only)\n"
                 "/restart - To restart the bot (Owner only)",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅ Back", callback_data="back_to_help"),
                 InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )

    elif data == "back_to_help":
        await help_command(client, query.message)
