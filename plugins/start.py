import os, asyncio, humanize
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, ChatAdminRequired
from bot import Bot
from config import ADMINS, OWNER_ID, SUDO_USERS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, FILE_AUTO_DELETE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, DB_URL, DB_NAME
from helper_func import subscribed, encode, decode, get_messages
from database.db_handler import get_force_sub_channel, refresh_db_handler, get_admins
from database.database import add_user, del_user, full_userbase, present_user
from plugins.cbb import check_force_sub   # Import the check_force_sub function
from plugins.refresh import refresh_database, refresh_force_sub_channels, cache_invite_links, refresh_command, refresh_auto_delete_time, refresh_admins
import pymongo
import random  # Import random to select a random photo


madflixofficials = FILE_AUTO_DELETE
jishudeveloper = madflixofficials
file_auto_delete = humanize.naturaldelta(jishudeveloper)

# List of photo URLs
photos = [
    "https://litter.catbox.moe/8ngis1.jpg",
    "https://litter.catbox.moe/21bhag.jpg",
    # Add more photo URLs as needed
]

@Bot.on_message(filters.command('start') & filters.private & subscribed)
@Bot.on_message(filters.command('start') & filters.group & subscribed)
async def start_command(client: Client, message: Message):
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
async def not_joined(client: Client, message: Message):
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

@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS + get_admins()))
@Bot.on_message(filters.command('users') & filters.group & filters.user(ADMINS + get_admins()))
async def get_users(client: Bot, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text="Processing...")
    users = await full_userbase()
    await msg.edit(f"{len(users)} Users Are Using This Bot")

@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("Use This Command As A Reply To Any Telegram Message With Out Any Spaces.")
        await asyncio.sleep(8)
        await msg.delete()

@Client.on_message(filters.command("fsubs") & filters.user([OWNER_ID] + ADMINS))
async def force_subs(client, message):
    channels = [get_force_sub_channel(1), get_force_sub_channel(2), get_force_sub_channel(3), get_force_sub_channel(4)]

    buttons = []
    for channel in channels:
        if channel and str(channel).startswith("-100"):  # Ensure it's a valid channel ID
            try:
                chat = await client.get_chat(chat_id=channel)  # Fetch channel details
                invite_link = await client.create_chat_invite_link(chat_id=channel)
                buttons.append([InlineKeyboardButton(chat.title, url=invite_link.invite_link)])  # Use channel name
            except Exception as e:
                print(f"Error generating invite link for {channel}: {e}")

    if not buttons:
        return await message.reply_text("No valid force subscription channels found!")

    # Add close button to the reply markup
    buttons.append([InlineKeyboardButton("🔒 Close", callback_data="close")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text("Here is the list of force subscription channels:", reply_markup=reply_markup)


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

    await message.reply_text(admin_text, disable_web_page_preview=True, reply_markup=reply_markup)

@Client.on_message(filters.command("admins") & filters.user([OWNER_ID] + ADMINS))
async def list_admins(client, message):
    unique_admins = list(set(ADMINS + get_admins()))  # Remove duplicate IDs
    admins_list = []

    for index, admin_id in enumerate(unique_admins, start=1):
        try:
            user = await client.get_users(admin_id)  # Fetch user details
            admin_name = f"[{user.first_name}]( tg://openmessage?user_id={admin_id} )"
        except Exception:
            admin_name = f"`{admin_id}` (Bot not started)"  # If user data not found

        admins_list.append(f"{index}. {admin_name} (`<code>{admin_id}</code>`)")
    
    admin_text = "👮‍♂️ Here is the list of bot admins:\n\n" + "\n".join(admins_list)

    # Add close button to the reply markup
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Close", callback_data="close")]])

    await message.reply_text(admin_text, disable_web_page_preview=True, reply_markup=reply_markup)


@Client.on_message(filters.private & filters.command("fpbroadcast") & filters.user([OWNER_ID] + ADMINS))
async def forward_broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Use this command as a reply to the message you want to forward.")

    query = await full_userbase()
    forward_msg = message.reply_to_message
    total, successful, blocked, deleted, unsuccessful = len(query), 0, 0, 0, 0

    pls_wait = await message.reply("<i>Forwarding message to all users... This may take some time.</i>")

    for chat_id in query:
        try:
            sent_msg = await forward_msg.forward(chat_id)
            successful += 1

            # Try to pin the message
            try:
                await client.pin_chat_message(chat_id, sent_msg.id)
            except ChatAdminRequired:
                print(f"Cannot pin message in {chat_id}, bot is not an admin.")

        except FloodWait as e:
            await asyncio.sleep(e.x)
            sent_msg = await forward_msg.forward(chat_id)
            successful += 1
            try:
                await client.pin_chat_message(chat_id, sent_msg.id)
            except ChatAdminRequired:
                print(f"Cannot pin message in {chat_id}, bot is not an admin.")

        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
            unsuccessful += 1
            continue

    status = f"""<b><u>✅ Forward Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""

    return await pls_wait.edit(status)

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
    await message.reply_text("The current auto delete timer is set to ",FILE_AUTO_DELETE," seconds.")


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
