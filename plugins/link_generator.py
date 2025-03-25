from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS, SUDO_USERS
from database.db_handler import get_admins
from helper_func import encode, get_message_id


async def get_valid_message(client, user_id, prompt_text):
    """Helper function to get a valid message or link from the DB channel."""
    while True:
        try:
            user_input = await client.ask(
                text=prompt_text,
                chat_id=user_id,
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except:
            return None  # Return None if no input is given within 60 seconds

        msg_id = await get_message_id(client, user_input)
        if msg_id:
            return msg_id
        else:
            await user_input.reply(
                "❌ Error\n\nThis Forwarded Post Is Not From My DB Channel Or This Link Is Not Taken From DB Channel",
                quote=True,
            )


async def generate_link(client, msg_id1, msg_id2=None):
    """Generate base64-encoded URL for single or batch message."""
    if msg_id2:
        string = f"get-{msg_id1 * abs(client.db_channel.id)}-{msg_id2 * abs(client.db_channel.id)}"
    else:
        string = f"get-{msg_id1 * abs(client.db_channel.id)}"
    
    base64_string = await encode(string)
    return f"https://t.me/{client.username}?start={base64_string}"


async def send_link_response(message, link):
    """Send generated link to user with share button."""
    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={link}")]]
    )
    await message.reply_text(
        f"<b>Here Is Your Link</b>\n\n{link}",
        quote=True,
        reply_markup=reply_markup,
    )


@Bot.on_message(filters.private & filters.command("batch"))
async def batch(client: Client, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        user_id = message.from_user.id

        # Get the first message
        f_msg_id = await get_valid_message(client, user_id, "Forward The First Message From DB Channel (With Quotes)..\n\nOr Send The DB Channel Post Link")
        if not f_msg_id:
            return

        # Get the last message
        s_msg_id = await get_valid_message(client, user_id, "Forward The Last Message From DB Channel (With Quotes)..\n\nOr Send The DB Channel Post Link")
        if not s_msg_id:
            return

        # Generate batch link and send
        link = await generate_link(client, f_msg_id, s_msg_id)
        await send_link_response(message, link)


@Bot.on_message(filters.private & filters.command("genlink"))
async def link_generator(client: Client, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        user_id = message.from_user.id

        # Get the message for single link
        msg_id = await get_valid_message(client, user_id, "Forward Message From The DB Channel (With Quotes)..\n\nOr Send The DB Channel Post link")
        if not msg_id:
            return

        # Generate link and send
        link = await generate_link(client, msg_id)
        await send_link_response(message, link)
