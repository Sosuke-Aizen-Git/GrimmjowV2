import asyncio
import re
import base64
import pymongo
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant, FloodWait
from config import FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, ADMINS, DB_URL, DB_NAME
from bot import Bot
from database.db_handler import get_force_sub_channel, get_admins

# Database connection
dbclient = pymongo.MongoClient(DB_URL)
database = dbclient[DB_NAME]
user_data = database["users"]

# Optimized force subscription check
async def is_subscribed(_, client, update):
    user_id = update.from_user.id
    if user_id in ADMINS + get_admins():
        return True

    channels = [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]
    active_channels = [ch for i, ch in enumerate(channels, start=1) if get_force_sub_channel(i)]

    for channel in active_channels:
        try:
            member = await client.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
                return False
        except UserNotParticipant:
            return False

    return True

# Encoding and decoding functions
async def encode(string: str) -> str:
    return base64.urlsafe_b64encode(string.encode()).decode().rstrip("=")

async def decode(base64_string: str) -> str:
    base64_string = base64_string.rstrip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode()
    return base64.urlsafe_b64decode(base64_bytes).decode()

# Fetch multiple messages efficiently
async def get_messages(client, message_ids):
    messages = []
    for i in range(0, len(message_ids), 200):
        batch = message_ids[i:i + 200]
        try:
            messages.extend(await client.get_messages(client.db_channel.id, batch))
        except FloodWait as e:
            await asyncio.sleep(e.x)
            messages.extend(await client.get_messages(client.db_channel.id, batch))
    return messages

# Extract message ID from forwarded messages or links
async def get_message_id(client, message):
    if message.forward_from_chat and message.forward_from_chat.id == client.db_channel.id:
        return message.forward_from_message_id
    if message.forward_sender_name or not message.text:
        return 0

    pattern = r"https://t.me/(?:c/)?([^/]+)/(\d+)"
    match = re.match(pattern, message.text)
    if not match:
        return 0

    channel_id, msg_id = match.groups()
    if channel_id.isdigit():
        return msg_id if f"-100{channel_id}" == str(client.db_channel.id) else 0
    return msg_id if channel_id == client.db_channel.username else 0

# Convert seconds to a readable time format
def get_readable_time(seconds: int) -> str:
    time_values = []
    time_units = ["s", "m", "h", "d"]
    for divisor in [60, 60, 24]:
        seconds, value = divmod(seconds, divisor)
        time_values.append(value)
        if seconds == 0:
            break
    return ":".join(f"{v}{u}" for v, u in zip(reversed(time_values), reversed(time_units)))

# Apply the filter
subscribed = filters.create(is_subscribed)
