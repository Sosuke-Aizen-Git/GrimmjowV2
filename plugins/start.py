import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatAdminRequired
from bot import Bot
from config import ADMINS, OWNER_ID, SUDO_USERS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, DB_URL, DB_NAME, PHOTOS
from helper_func import subscribed, encode, decode, get_messages
from database.db_handler import get_force_sub_channel, refresh_db_handler, get_admins, get_auto_delete_time
from database.database import add_user, del_user, full_userbase, present_user
from plugins.cbb import check_force_sub   # Import the check_force_sub function
from plugins.refresh import refresh_database, refresh_force_sub_channels, cache_invite_links, refresh_command, refresh_auto_delete_time, refresh_admins
import pymongo
import asyncio
import time
import random  # Import random to select a random photo


file_auto_delete = humanize.naturaldelta(get_auto_delete_time())


@Bot.on_message(filters.command('start') & subscribed)
async def start_command(client: Client, message: Message):
    Emoji = await message.reply("⏳")
    await asyncio.sleep(1)  # Waits for 5 seconds before deleting
    await Emoji.delete()
    await message.react("👍")
    
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

        madflix_msgs = []  # List to keep track of sent messages

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

        k = await client.send_message(chat_id=message.from_user.id, text=f"<blockquote><b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete} (Due To Copyright Issue Or Other Reasons).\n\n📌 Please Forward This Video / File To Somewhere Else And Start Downloading There.</blockquote>")

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
        random_photo = random.choice(PHOTOS)

        await client.send_photo(
            chat_id=message.chat.id,
            photo=random_photo,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ), reply_markup=reply_markup
        )
        return
    

@Bot.on_message(filters.command('start'))
async def not_joined(client: Client, message: Message):
    await message.react("👎")

    # Send initial message before checking not_join
    
    # Send animated "Checking..." message
    animation_message = await message.reply("🔄 Checking...")
    for _ in range(3):
        await asyncio.sleep(1)
        await animation_message.edit(f"🔄 Checking{'.' * (_ % 3 + 1)}")

    # Send "Please Wait..." message
    temp_msg = await message.reply("Please Wait...")

    # Refresh the invite links and force sub channels
    await refresh_force_sub_channels()

    buttons = []
    for i in range(1, 5):
        invitelink = (await client.get_chat(get_force_sub_channel(i))).invite_link if get_force_sub_channel(i) else None
        if invitelink:
            buttons.append([InlineKeyboardButton(text=f"Join Channel {i}", url=invitelink)])

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
    await animation_message.delete()

    # Check if user has joined all force sub channels before sending force sub message
    if not await check_force_sub(client, message.from_user.id):
        random_photo = random.choice(PHOTOS)
        await client.send_photo(
            chat_id=message.chat.id,
            photo=random_photo,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ), reply_markup=InlineKeyboardMarkup(buttons),
        )
        return

    # Delete the animation message
    

    # User has joined all channels, proceed with start command
    await start_command(client, message)


@Bot.on_message(filters.command('users') & filters.private)
@Bot.on_message(filters.command('users') & filters.group)
async def get_users(client: Bot, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        msg = await client.send_message(chat_id=message.chat.id, text="Processing...")
        users = await full_userbase()
        await msg.edit(f"{len(users)} Users Are Using This Bot")
    else:
        await message.reply_text("You are not an authorized user!")


async def broadcast_message(client, message, pin=False, forward=False):
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await message.reply_text("🚫 You are not an authorized user!")

    if not message.reply_to_message:
        return await message.reply("❌ Use this command as a reply to the message you want to broadcast.")

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total, successful, blocked, deleted, unsuccessful = len(query), 0, 0, 0, 0

    pls_wait = await message.reply("<i>Broadcasting message... Please wait.</i>")

    start_time = time.time()  # Start time

    for chat_id in query:
        try:
            if forward:
                sent_msg = await broadcast_msg.forward(chat_id)
            else:
                sent_msg = await broadcast_msg.copy(chat_id)

            successful += 1

            if pin:
                try:
                    await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
                except Exception:
                    pass  # Ignore pinning errors

        except FloodWait as e:
            await asyncio.sleep(e.x)
            continue  # Retry after waiting

        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1

        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1

        except Exception:
            unsuccessful += 1
            continue

    end_time = time.time()  # End time
    total_time = round(end_time - start_time, 2)  # Calculate total time taken

    status = f"""<b><u>✅ Broadcast Completed</u></b>

<b>Total Users:</b> <code>{total}</code>
<b>Successful:</b> <code>{successful}</code>
<b>Blocked Users:</b> <code>{blocked}</code>
<b>Deleted Accounts:</b> <code>{deleted}</code>
<b>Unsuccessful:</b> <code>{unsuccessful}</code>
<b>Total Time Taken:</b> <code>{total_time} seconds</code>"""

    await pls_wait.edit(status)
    
# Normal broadcast
@Bot.on_message(filters.private & filters.command('broadcast'))
async def send_text(client, message):
    await broadcast_message(client, message, pin=False, forward=False)

# Broadcast & pin message
@Bot.on_message(filters.private & filters.command('pbroadcast'))
async def send_pinned_broadcast(client, message):
    await broadcast_message(client, message, pin=True, forward=False)

# Forwarded message broadcast
@Bot.on_message(filters.private & filters.command('fpbroadcast'))
async def forward_broadcast(client, message):
    await broadcast_message(client, message, pin=False, forward=True)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("fsubs"))
async def force_subs(client, message):
    temp_mssg = await message.reply("<blockquote>Fetching force subscription channels...</blockquote>")
    
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await temp_mssg.edit("<blockquote>You are not authorized to perform this action.</blockquote>")

    channels = [get_force_sub_channel(i) for i in range(1, 5)]
    buttons = []
    cache_invites = {}
    channel_info = ""

    for idx, channel in enumerate(channels, start=1):
        if channel and str(channel).startswith("-100"):  # Ensure valid channel ID
            try:
                if channel in cache_invites:
                    invite_link = cache_invites[channel]
                else:
                    chat = await client.get_chat(chat_id=channel)
                    invite_link = await client.create_chat_invite_link(chat_id=channel)
                    cache_invites[channel] = invite_link.invite_link  # Cache the invite link
                
                buttons.append([InlineKeyboardButton(chat.title, url=invite_link.invite_link)])
                channel_info += f"<blockquote>Force Sub Channel {idx}:</blockquote>\n<pre>{channel}</pre>\n"
            except Exception as e:
                logger.error(f"Error generating invite link for {channel}: {e}")

    if not buttons:
        return await temp_mssg.edit("<blockquote>No valid force subscription channels found!</blockquote>")

    # Add Close button
    buttons.append([InlineKeyboardButton("🔒 Close", callback_data="close")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await temp_mssg.edit(f"<blockquote>Here is the list of force subscription channels:</blockquote>\n\n{channel_info}", reply_markup=reply_markup)

# Function to handle file deletion
async def delete_files(messages, client, k):
    await asyncio.sleep(get_auto_delete_time())  # Wait for the duration specified in config.py
    for msg in messages:
        if msg is not None:  # Ensure msg is not None
            try:
                await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            except Exception as e:
                print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")
    await k.edit_text("Your Video / File Is Successfully Deleted ✅")

     

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@Client.on_message(filters.command("admins"))
async def list_admins(client, message):
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await message.reply_text("<blockquote>You are not authorized to perform this action.</blockquote>")

    temp_mssg = await message.reply_text("🔍 Fetching admins...")

    unique_admins = list(set(SUDO_USERS + get_admins()))  # Remove duplicate IDs
    admins_list = []

    for index, admin_id in enumerate(unique_admins, start=1):
        try:
            user = await client.get_users(admin_id)  # Fetch user details
            admin_name = f"<a href='tg://openmessage?user_id={admin_id}'>{user.first_name}</a>"
        except Exception:
            admin_name = "<b>Bot not started</b>"

        admins_list.append(f"<b>{index}.</b> {admin_name} : <pre>{admin_id}</pre>")

    if not admins_list:
        return await temp_mssg.edit_text("<blockquote>No admins found!</blockquote>")

    admin_text = "<b>👮‍♂️ Here is the list of bot admins:</b>\n\n" + "\n".join(admins_list)

    # Close button
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Close", callback_data="close")]])

    await temp_mssg.edit_text(admin_text, disable_web_page_preview=True, reply_markup=reply_markup)


@Bot.on_message(filters.command('id') & filters.private)
@Bot.on_message(filters.command('id') & filters.group)
async def get_id(client: Bot, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
        user_name = user.first_name
    else:
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            user = message.from_user
            user_id = user.id
            user_name = user.first_name
        else:
            username = parts[1].strip()
            try:
                user = await client.get_users(username)
                user_id = user.id
                user_name = user.first_name
            except Exception as e:
                await message.reply_text(f"User {username} not found.\nError: {e}")
                return

    await message.reply_text(f"User {user_name}'s ID: <code>{user_id}</code>", quote=True)

# Add this import statement at the top if not already present
from config import FILE_AUTO_DELETE


# Add the following function in `start.py` to handle the /autodel command
@Bot.on_message(filters.command('autodel') & filters.private)
@Bot.on_message(filters.command('autodel') & filters.group)
async def autodel_command(client: Client, message: Message):
    await message.reply_text(f"The current auto delete timer is set to {(get_auto_delete_time())} seconds.")


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
