import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ParseMode
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatAdminRequired
from bot import Bot
from config import ADMINS, OWNER_ID, SUDO_USERS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, DB_URL, DB_NAME
from helper_func import subscribed, encode, decode, get_messages
from database.db_handler import get_force_sub_channel, refresh_db_handler, get_admins, get_auto_delete_time
from database.database import add_user, del_user, full_userbase, present_user
from plugins.cbb import check_force_sub   # Import the check_force_sub function
from plugins.refresh import refresh_database, refresh_force_sub_channels, cache_invite_links, refresh_command, refresh_auto_delete_time, refresh_admins
import pymongo
import random  # Import random to select a random photo


file_auto_delete = humanize.naturaldelta(get_auto_delete_time())

photos = [
    "https://litter.catbox.moe/8ngis1.jpg",
    "https://litter.catbox.moe/21bhag.jpg",
    # Add more photo URLs as needed
]

@Bot.on_message(filters.command('start') & filters.private & subscribed)
@Bot.on_message(filters.command('start') & filters.group & subscribed)
async def start_command(client: Bot, message: Message):
    id = message.from_user.id
    if not await present_user(id):
        try:
            await add_user(id)
        except:
            pass
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return
        string = await decode(base64_string)
        argument = string.split("-")
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except:
                return
            if start <= end:
                ids = range(start, end + 1)
            else:
                ids = []
                i = start
                while True:
                    ids.append(i)
                    i -= 1
                    if i < end:
                        break
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except:
                return
        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something Went Wrong..!")
            return
        await temp_msg.delete()

        madflix_msgs = []

        for msg in messages:
            if bool(CUSTOM_CAPTION) & bool(msg.document):
                caption = CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, filename=msg.document.file_name)
            else:
                caption = "" if not msg.caption else msg.caption.html

            if DISABLE_CHANNEL_BUTTON:
                reply_markup = msg.reply_markup
            else:
                reply_markup = None

            try:
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)

            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)

            except:
                pass

        k = await client.send_message(chat_id=message.from_user.id, text=f"<b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issue Or Other Reasons).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.")

        # Schedule the file deletion
        asyncio.create_task(delete_files(madflix_msgs, client, k))

        return
    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("😊 About Me", callback_data="about"),
                    InlineKeyboardButton("🔒 Close", callback_data="close")
                ]
            ]
        )

        # Select a random photo from the list
        random_photo = random.choice(photos)

        await client.send_photo(
            chat_id=message.chat.id,
            photo=random_photo,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup
        )
        return

@Bot.on_message(filters.command('start') & filters.private)
@Bot.on_message(filters.command('start') & filters.group)
async def not_joined(client: Bot, message: Message):
    # Send "Please Wait..." message
    temp_msg = await message.reply("Please Wait...")

    # Refresh the invite links and force sub channels
    await refresh_force_sub_channels()

    client.invitelink = (await client.get_chat(get_force_sub_channel(1))).invite_link if FORCE_SUB_CHANNEL_1 else None
    client.invitelink2 = (await client.get_chat(get_force_sub_channel(2))).invite_link if FORCE_SUB_CHANNEL_2 else None
    client.invitelink3 = (await client.get_chat(get_force_sub_channel(3))).invite_link if FORCE_SUB_CHANNEL_3 else None
    client.invitelink4 = (await client.get_chat(get_force_sub_channel(4))).invite_link if FORCE_SUB_CHANNEL_4 else None

    buttons = [
        [
            InlineKeyboardButton(text="Join Channel 1", url=client.invitelink),
            InlineKeyboardButton(text="Join Channel 2", url=client.invitelink2),
        ],
        [
            InlineKeyboardButton(text="Join Channel 3", url=client.invitelink3),
            InlineKeyboardButton(text="Join Channel 4", url=client.invitelink4),
        ]
    ]
    try:
        buttons.append(
            [
                InlineKeyboardButton(
                    text='Try Again',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ]
        )
    except IndexError:
        pass

    await temp_msg.delete()  # Delete the "Please Wait..." message

    # Check if user has joined all force sub channels before sending force sub message
    if not await check_force_sub(client, message.from_user.id):
        await message.reply(
            text=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
            disable_web_page_preview=True
        )
        return

    # User has joined all channels, proceed with start command
    await start_command(client, message)



# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
