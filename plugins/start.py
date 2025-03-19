import os, asyncio, humanize, logging, time, random
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatAdminRequired
from bot import Bot
from config import (
    ADMINS, OWNER_ID, SUDO_USERS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON,
    PROTECT_CONTENT, FILE_AUTO_DELETE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3,
    FORCE_SUB_CHANNEL_4, DB_URL, DB_NAME, PHOTOS
)
from helper_func import subscribed, encode, decode, get_messages
from database.db_handler import get_force_sub_channel, refresh_db_handler, get_admins, get_auto_delete_time
from database.database import add_user, del_user, full_userbase, present_user
from plugins.cbb import check_force_sub
from plugins.refresh import refresh_force_sub_channels, cache_invite_links

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_auto_delete = humanize.naturaldelta(get_auto_delete_time())

# =============================== #
# START COMMAND - USER JOIN CHECK #
# =============================== #
@Bot.on_message(filters.command('start') & subscribed)
async def start_command(client: Client, message: Message):
    Emoji = await message.reply("⏳")
    await asyncio.sleep(1)
    await Emoji.delete()
    await message.react("👍")

    user_id = message.from_user.id
    if not await present_user(user_id):
        await add_user(user_id)

    text = message.text
    if len(text) > 7:
        await handle_inline_start(client, message, text)
    else:
        await send_welcome(client, message)


async def handle_inline_start(client, message, text):
    try:
        base64_string = text.split(" ", 1)[1]
        decoded_data = await decode(base64_string)
        argument = decoded_data.split("-")

        ids = extract_message_ids(argument, client)
        if not ids:
            return

        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply_text("Something Went Wrong..!")
            return
        await temp_msg.delete()

        madflix_msgs = await send_messages(client, messages, message.from_user.id)
        await schedule_deletion(madflix_msgs, client, message)

    except Exception as e:
        logger.error(f"Error in inline start: {e}")


def extract_message_ids(argument, client):
    try:
        if len(argument) == 3:
            start, end = map(int, [int(argument[1]) / abs(client.db_channel.id), int(argument[2]) / abs(client.db_channel.id)])
            return range(start, end + 1) if start <= end else range(start, end - 1, -1)
        elif len(argument) == 2:
            return [int(int(argument[1]) / abs(client.db_channel.id))]
    except:
        pass
    return []


async def send_messages(client, messages, user_id):
    madflix_msgs = []
    for msg in messages:
        caption = CUSTOM_CAPTION.format(previouscaption=msg.caption.html if msg.caption else "", filename=msg.document.file_name) if CUSTOM_CAPTION and msg.document else msg.caption.html or ""
        reply_markup = None if DISABLE_CHANNEL_BUTTON else msg.reply_markup

        try:
            madflix_msg = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            madflix_msgs.append(madflix_msg)
        except FloodWait as e:
            await asyncio.sleep(e.x)
            madflix_msg = await msg.copy(chat_id=user_id, caption=caption, parse_mode=ParseMode.HTML, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
            madflix_msgs.append(madflix_msg)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    return madflix_msgs


async def schedule_deletion(messages, client, message):
    notification = await client.send_message(chat_id=message.from_user.id, text=f"<blockquote><b>❗️ <u>IMPORTANT</u> ❗️</b>\n\nThis Video / File Will Be Deleted In {file_auto_delete}.\n\n📌 Please Forward This Video / File To Somewhere Else.</blockquote>")
    asyncio.create_task(delete_files(messages, client, notification))


async def delete_files(messages, client, notification):
    await asyncio.sleep(get_auto_delete_time())
    for msg in messages:
        if msg:
            try:
                await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
            except Exception as e:
                logger.error(f"Failed to delete message {msg.id}: {e}")
    await notification.edit_text("Your Video / File Is Successfully Deleted ✅")


async def send_welcome(client, message):
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("😊 About Me", callback_data="about"), InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    random_photo = random.choice(PHOTOS)

    await client.send_photo(
        chat_id=message.chat.id,
        photo=random_photo,
        caption=START_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=f"@{message.from_user.username}" if message.from_user.username else None,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=reply_markup
    )


# ============================= #
# USER BROADCAST & ADMIN PANEL  #
# ============================= #
async def broadcast_message(client, message, pin=False, forward=False):
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await message.reply_text("🚫 You are not an authorized user!")

    if not message.reply_to_message:
        return await message.reply("❌ Use this command as a reply to the message you want to broadcast.")

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total, successful, blocked, deleted, unsuccessful = len(query), 0, 0, 0, 0
    pls_wait = await message.reply("<i>Broadcasting message... Please wait.</i>")

    start_time = time.time()
    for chat_id in query:
        try:
            sent_msg = await (broadcast_msg.forward(chat_id) if forward else broadcast_msg.copy(chat_id))
            successful += 1
            if pin:
                await pin_message(client, chat_id, sent_msg)
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except (UserIsBlocked, InputUserDeactivated):
            await del_user(chat_id)
            blocked += 1 if isinstance(e, UserIsBlocked) else deleted + 1
        except Exception:
            unsuccessful += 1
    await summarize_broadcast(pls_wait, total, successful, blocked, deleted, unsuccessful, start_time)


async def pin_message(client, chat_id, sent_msg):
    try:
        await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
    except Exception:
        pass


async def summarize_broadcast(pls_wait, total, successful, blocked, deleted, unsuccessful, start_time):
    total_time = round(time.time() - start_time, 2)
    status = f"""<b><u>✅ Broadcast Completed</u></b>
<b>Total Users:</b> <code>{total}</code>
<b>Successful:</b> <code>{successful}</code>
<b>Blocked Users:</b> <code>{blocked}</code>
<b>Deleted Accounts:</b> <code>{deleted}</code>
<b>Unsuccessful:</b> <code>{unsuccessful}</code>
<b>Total Time Taken:</b> <code>{total_time} seconds</code>"""
    await pls_wait.edit(status)


@Bot.on_message(filters.private & filters.command('broadcast'))
async def send_text(client, message):
    await broadcast_message(client, message, pin=False, forward=False)


@Bot.on_message(filters.private & filters.command('pbroadcast'))
async def send_pinned_broadcast(client, message):
    await broadcast_message(client, message, pin=True, forward=False)


@Bot.on_message(filters.private & filters.command('fpbroadcast'))
async def forward_broadcast(client, message):
    await broadcast_message(client, message, pin=False, forward=True)


# ======================== #
# USER / ADMIN COMMANDS    #
# ======================== #
@Bot.on_message(filters.command('users') & (filters.private | filters.group))
async def get_users(client: Bot, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        users = await full_userbase()
        await message.reply_text(f"{len(users)} Users Are Using This Bot")
    else:
        await message.reply_text("You are not an authorized user!")


@Bot.on_message(filters.command('id') & (filters.private | filters.group))
async def get_id(client: Bot, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.text.split()) == 1:
        user = message.from_user
    else:
        try:
            username = message.text.split(maxsplit=1)[1].strip()
            user = await client.get_users(username)
        except Exception as e:
            return await message.reply_text(f"User {username} not found.\nError: {e}")

    await message.reply_text(f"User {user.first_name}'s ID: <code>{user.id}</code>", quote=True)


@Bot.on_message(filters.command('autodel') & (filters.private | filters.group))
async def autodel_command(client: Client, message: Message):
    await message.reply_text(f"The current auto delete timer is set to {get_auto_delete_time()} seconds.")


@Bot.on_message(filters.command('fsubs'))
async def force_subs(client, message):
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await message.reply_text("<blockquote>You are not authorized to perform this action.</blockquote>")

    temp_mssg = await message.reply("<blockquote>Fetching force subscription channels...</blockquote>")
    buttons, channel_info = await get_force_sub_channels(client)

    if not buttons:
        return await temp_mssg.edit("<blockquote>No valid force subscription channels found!</blockquote>")

    buttons.append([InlineKeyboardButton("🔒 Close", callback_data="close")])
    await temp_mssg.edit(f"<blockquote>Here is the list of force subscription channels:</blockquote>\n\n{channel_info}", reply_markup=InlineKeyboardMarkup(buttons))


async def get_force_sub_channels(client):
    buttons, channel_info, cache_invites = [], "", {}
    for i in range(1, 5):
        channel = get_force_sub_channel(i)
        if channel and str(channel).startswith("-100"):
            try:
                invite_link = cache_invites.get(channel) or await client.create_chat_invite_link(chat_id=channel)
                chat = await client.get_chat(chat_id=channel)
                buttons.append([InlineKeyboardButton(chat.title, url=invite_link.invite_link)])
                channel_info += f"<blockquote>Force Sub Channel {i}:</blockquote>\n<pre>{channel}</pre>\n"
            except Exception as e:
                logger.error(f"Error generating invite link for {channel}: {e}")
    return buttons, channel_info
