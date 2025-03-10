import os, asyncio, humanize, random, pymongo
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import (ADMINS, SUDO_USERS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, 
                    FILE_AUTO_DELETE, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, PHOTOS)
from helper_func import subscribed, encode, decode, get_messages
from database.db_handler import get_force_sub_channel, get_admins, get_auto_delete_time
from database.database import add_user, del_user, full_userbase, present_user
from plugins.cbb import check_force_sub

file_auto_delete = humanize.naturaldelta(get_auto_delete_time())

@Bot.on_message(filters.command('start') & subscribed)
async def start_command(client: Client, message: Message):
    await message.react("👍")
    user_id = message.from_user.id

    if not await present_user(user_id):
        await add_user(user_id)

    if " " in message.text:
        try:
            base64_string = message.text.split(" ", 1)[1]
            string = await decode(base64_string)
            ids = list(map(lambda x: int(int(x) / abs(client.db_channel.id)), string.split("-")[1:]))
        except:
            return
        
        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except:
            await message.reply("Something Went Wrong..!")
            return
        await temp_msg.delete()

        madflix_msgs = []
        for msg in messages:
            caption = CUSTOM_CAPTION.format(previouscaption=msg.caption.html if msg.caption else "", filename=msg.document.file_name) if CUSTOM_CAPTION and msg.document else msg.caption or ""
            reply_markup = None if DISABLE_CHANNEL_BUTTON else msg.reply_markup
            
            try:
                madflix_msg = await msg.copy(message.from_user.id, caption=caption, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                madflix_msg = await msg.copy(message.from_user.id, caption=caption, reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                madflix_msgs.append(madflix_msg)

        warning_msg = await client.send_message(message.from_user.id, f"❗ **IMPORTANT** ❗\n\nThis file will be deleted in {file_auto_delete}. Forward and download it elsewhere.")

        asyncio.create_task(delete_files(madflix_msgs, client, warning_msg))
        return

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("😊 About Me", callback_data="about"), InlineKeyboardButton("🔒 Close", callback_data="close")]])
    await client.send_photo(message.chat.id, random.choice(PHOTOS), caption=START_MSG.format(
        first=message.from_user.first_name, last=message.from_user.last_name, username=f'@{message.from_user.username}' if message.from_user.username else None, mention=message.from_user.mention, id=message.from_user.id),
        reply_markup=reply_markup)

async def delete_files(messages, client, warning_msg):
    await asyncio.sleep(get_auto_delete_time())
    await asyncio.gather(*[client.delete_messages(msg.chat.id, [msg.id]) for msg in messages if msg])
    await warning_msg.edit_text("Your Video / File Is Successfully Deleted ✅")

@Bot.on_message(filters.command("admins"))
async def list_admins(client, message):
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await message.reply("You are not an authorized user!")

    unique_admins = list(set(SUDO_USERS + get_admins()))
    admin_details = await asyncio.gather(*[fetch_admin_details(client, admin) for admin in unique_admins])

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Close", callback_data="close")]])
    await message.reply("👮‍♂️ **Bot Admins:**\n\n" + "\n".join(admin_details), disable_web_page_preview=True, reply_markup=reply_markup)

async def fetch_admin_details(client, admin_id):
    try:
        user = await client.get_users(admin_id)
        return f"- [{user.first_name}](tg://user?id={admin_id}) (`{admin_id}`)"
    except:
        return f"- `{admin_id}` (Bot not started)"

@Bot.on_message(filters.command('id'))
async def get_id(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else await client.get_users(message.command[1]) if len(message.command) > 1 else message.from_user
    await message.reply(f"User {user.first_name}'s ID: `{user.id}`")

@Bot.on_message(filters.command('autodel'))
async def autodel_command(client, message):
    await message.reply(f"Auto-delete timer: {get_auto_delete_time()} seconds.")

async def broadcast_message(client, message, pin=False, forward=False):
    if message.from_user.id not in get_admins() + SUDO_USERS:
        return await message.reply("🚫 You are not an authorized user!")

    if not message.reply_to_message:
        return await message.reply("❌ Use this command as a reply to the message you want to broadcast.")

    query = await full_userbase()
    broadcast_msg = message.reply_to_message
    total, success, blocked, deleted, failed = len(query), 0, 0, 0, 0

    pls_wait = await message.reply("Broadcasting message... Please wait.")

    async def send_to_user(chat_id):
        nonlocal success, blocked, deleted, failed
        try:
            sent_msg = await (broadcast_msg.forward(chat_id) if forward else broadcast_msg.copy(chat_id))
            success += 1
            if pin:
                try:
                    await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
                except:
                    pass
        except FloodWait as e:
            await asyncio.sleep(e.x)
            await send_to_user(chat_id)
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except:
            failed += 1

    await asyncio.gather(*[send_to_user(chat_id) for chat_id in query])

    await pls_wait.edit(f"""✅ **Broadcast Completed**\n\n**Total Users:** `{total}`\n**Successful:** `{success}`\n**Blocked:** `{blocked}`\n**Deleted:** `{deleted}`\n**Failed:** `{failed}`""")

@Bot.on_message(filters.private & filters.command('broadcast'))
async def send_text(client, message):
    await broadcast_message(client, message, pin=False, forward=False)

@Bot.on_message(filters.private & filters.command('pbroadcast'))
async def send_pinned_broadcast(client, message):
    await broadcast_message(client, message, pin=True, forward=False)

@Bot.on_message(filters.private & filters.command('fpbroadcast'))
async def forward_broadcast(client, message):
    await broadcast_message(client, message, pin=False, forward=True)
