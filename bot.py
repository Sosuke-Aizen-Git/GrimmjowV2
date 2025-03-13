import asyncio
from aiohttp import web
from plugins import web_server
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import API_HASH, API_ID, LOGGER, BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, CHANNEL_ID, PORT
from utils import update_saved_button_state
from pymongo import MongoClient
from threading import Thread
import os

#######################
# CONFIGURATION
#######################
USERBOT_STRING = "your_userbot_string"  # Your Userbot string session
MONGO_URI = "mongodb://localhost:27017"  # MongoDB connection URI
DB_NAME = "YourDB"
COLLECTION_NAME = "channels"

#######################
# MONGODB SETUP
#######################
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
channels_collection = db[COLLECTION_NAME]

def save_channels(channels):
    """Save or update the channels list in MongoDB."""
    channels_collection.update_one({"_id": "channels"}, {"$set": {"list": channels}}, upsert=True)

def get_channels():
    """Retrieve the saved channels from MongoDB."""
    doc = channels_collection.find_one({"_id": "channels"})
    return doc.get("list", []) if doc else []

#######################
# FLASK APP (FOR UPTIME MONITORING)
#######################
from flask import Flask, jsonify
flask_app = Flask(__name__)

@flask_app.route('/uptime', methods=['GET'])
def uptime():
    return jsonify({"status": "ok"}), 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("FLASK_PORT", 5000)))

#######################
# BOT & USERBOT
#######################
class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_id=API_ID,
            api_hash=API_HASH,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.userbot = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=USERBOT_STRING)

    async def start(self):
        await super().start()
        await self.userbot.start()  # Start userbot here!
        
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        # Setup force subscription channels
        for i, channel in enumerate([FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4], start=1):
            if channel:
                try:
                    link = (await self.get_chat(channel)).invite_link
                    if not link:
                        await self.export_chat_invite_link(channel)
                        link = (await self.get_chat(channel)).invite_link
                    setattr(self, f"invitelink{i}", link)
                except Exception as e:
                    self.LOGGER(__name__).warning(f"Bot Can't Export Invite link From Force Sub Channel {i}: {e}")
                    sys.exit()

        # Check if bot is admin in the database channel
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            hey_message = await self.send_message(chat_id=db_channel.id, text="Hey 👋")
            asyncio.create_task(self.delete_message_after_delay(db_channel.id, hey_message.id, 5))
        except Exception as e:
            self.LOGGER(__name__).warning(f"Error accessing DB Channel: {e}")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info("✅ Bot Running!\n\nCreated By \nhttps://t.me/Madflix_Bots")

        # Notify restart
        saving_message = await self.send_message(chat_id=CHANNEL_ID, text="Bot restarted successfully.")
        asyncio.create_task(self.delete_message_after_delay(CHANNEL_ID, saving_message.id, 30))

        # Start Flask in a new thread
        Thread(target=run_flask).start()

        # Start web server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        # Call update function after bot starts
        await update_saved_button_state(saving_message)

    async def delete_message_after_delay(self, chat_id, message_id, delay):
        await asyncio.sleep(delay)
        await self.delete_messages(chat_id, message_id)

    async def stop(self, *args):
        await self.userbot.stop()  # Stop the userbot when the bot stops
        await super().stop()
        self.LOGGER(__name__).info("❌ Bot Stopped...")

#######################
# RUN BOT
#######################
if __name__ == "__main__":
    bot = Bot()
    bot.run()
