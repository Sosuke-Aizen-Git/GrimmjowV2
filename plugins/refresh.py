from bot import Bot
from pyrofork import Client, filters, __version__
from database.db_handler import get_force_sub_channel, refresh_db_handler, get_admins, get_auto_delete_time
from database.database import add_user, del_user, full_userbase, present_user
from config import OWNER_ID, SUDO_USERS, DB_URL, DB_NAME
import pymongo

async def refresh_database():
    global dbclient, database, user_data
    dbclient = pymongo.MongoClient(DB_URL)
    database = dbclient[DB_NAME]
    user_data = database['users']
    return

async def refresh_force_sub_channels():
    global FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4
    FORCE_SUB_CHANNEL_1 = get_force_sub_channel(1)
    FORCE_SUB_CHANNEL_2 = get_force_sub_channel(2)
    FORCE_SUB_CHANNEL_3 = get_force_sub_channel(3)
    FORCE_SUB_CHANNEL_4 = get_force_sub_channel(4)
    await cache_invite_links()

async def cache_invite_links():
    global invite_links_cache
    channels = [FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4]
    for index, channel in enumerate(channels, start=1):
        if channel:
            try:
                chat = await Bot.get_chat(chat_id=channel)
                invite_links_cache[f'link{index}'] = chat.invite_link or await Bot.export_chat_invite_link(chat_id=channel)
            except Exception as e:
                print(f"Error generating invite link for {channel}: {e}")


dbclient = pymongo.MongoClient(DB_URL)
database = dbclient[DB_NAME]
user_data = database['users']

invite_links_cache = {}

async def refresh_database():
    global dbclient, database, user_data
    dbclient = pymongo.MongoClient(DB_URL)
    database = dbclient[DB_NAME]
    user_data = database['users']
    return

from database.db_handler import get_admins, get_auto_delete_time

async def refresh_admins():
    global ADMINS
    ADMINS = get_admins()

async def refresh_auto_delete_time():
    global FILE_AUTO_DELETE
    FILE_AUTO_DELETE = get_auto_delete_time()

@Bot.on_message(filters.command('refresh') & filters.private & filters.user([OWNER_ID] + SUDO_USERS))
@Bot.on_message(filters.command('refresh') & filters.group & filters.user([OWNER_ID] + SUDO_USERS))
async def refresh_command(client, message):
    await refresh_database()
    await refresh_admins()
    await refresh_db_handler()
    await refresh_auto_delete_time()
    await message.reply_text("Database and force sub channels have been updated successfully with the latest changes.")
