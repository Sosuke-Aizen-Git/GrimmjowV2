from aiohttp import web
from plugins import web_server
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from config import API_HASH, API_ID, LOGGER, BOT_TOKEN, TG_BOT_WORKERS, FORCE_SUB_CHANNEL_1, FORCE_SUB_CHANNEL_2, FORCE_SUB_CHANNEL_3, FORCE_SUB_CHANNEL_4, CHANNEL_ID, PORT, ADMINS, SUDO_USERS, OWNER_ID
import pyrogram.utils
from utils import update_saved_button_state
import asyncio
from plugins import logs
from flask import Flask, jsonify
from threading import Thread
import os

pyrogram.utils.MIN_CHANNEL_ID = -1009999999999

# Define saving_message as a global variable
saving_message = None

# Create Flask app
flask_app = Flask(__name__)

@flask_app.route('/uptime', methods=['GET'])
def uptime():
    return jsonify({"status": "ok"}), 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=int(os.environ.get("FLASK_PORT", 5000)))

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        global saving_message  # Ensure saving_message is accessible
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL_1:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL_1)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL_1)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL_1)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot Can't Export Invite link From Force Sub Channel 1!")
                self.LOGGER(__name__).warning("Please Double Check The FORCE_SUB_CHANNEL_1 Value And Make Sure Bot Is Admin In Channel With Invite Users Via Link Permission, Current Force Sub Channel 1 Value: {FORCE_SUB_CHANNEL_1}")
                self.LOGGER(__name__).info("\nBot Stopped. https://t.me/MadflixBots_Support For Support")
                sys.exit()

        if FORCE_SUB_CHANNEL_2:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL_2)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL_2)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL_2)).invite_link
                self.invitelink2 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot Can't Export Invite link From Force Sub Channel 2!")
                self.LOGGER(__name__).warning("Please Double Check The FORCE_SUB_CHANNEL_2 Value And Make Sure Bot Is Admin In Channel With Invite Users Via Link Permission, Current Force Sub Channel 2 Value: {FORCE_SUB_CHANNEL_2}")
                self.LOGGER(__name__).info("\nBot Stopped. https://t.me/MadflixBots_Support For Support")
                sys.exit()

        if FORCE_SUB_CHANNEL_3:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL_3)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL_3)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL_3)).invite_link
                self.invitelink3 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot Can't Export Invite link From Force Sub Channel 3!")
                self.LOGGER(__name__).warning("Please Double Check The FORCE_SUB_CHANNEL_3 Value And Make Sure Bot Is Admin In Channel With Invite Users Via Link Permission, Current Force Sub Channel 3 Value: {FORCE_SUB_CHANNEL_3}")
                self.LOGGER(__name__).info("\nBot Stopped. https://t.me/MadflixBots_Support For Support")
                sys.exit()

        if FORCE_SUB_CHANNEL_4:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL_4)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL_4)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL_4)).invite_link
                self.invitelink4 = link
            except Exception as a:
                self.LOGGER(__name__).warning(a)
                self.LOGGER(__name__).warning("Bot Can't Export Invite link From Force Sub Channel 4!")
                self.LOGGER(__name__).warning("Please Double Check The FORCE_SUB_CHANNEL_4 Value And Make Sure Bot Is Admin In Channel With Invite Users Via Link Permission, Current Force Sub Channel 4 Value: {FORCE_SUB_CHANNEL_4}")
                self.LOGGER(__name__).info("\nBot Stopped. https://t.me/MadflixBots_Support For Support")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            await self.send_message(chat_id=db_channel.id, text="Hey 🖐")
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure Bot Is Admin In DB Channel, And Double Check The CHANNEL_ID Value, Current Value: {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/MadflixBots_Support For Support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated By \nhttps://t.me/Madflix_Bots")
        self.LOGGER(__name__).info(f"""ミ💖 MADFLIX BOTZ 💖彡""")
        self.username = usr_bot_me.username

        # Send restarted message
        saving_message = await self.send_message(chat_id=CHANNEL_ID, text="Bot restarted successfully.")

        # Notify all sudo users and the owner that changes are saved
        admin_message = "All changes are saved."
        for user in SUDO_USERS + [OWNER_ID]:
            try:
                await self.send_message(chat_id=user, text=admin_message)
            except Exception as e:
                self.LOGGER(__name__).warning(f"Failed to send message to user {user}: {e}")

        # Start Flask app in a new thread
        Thread(target=run_flask).start()

        # web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        # Call the update_saved_button_state function after the bot starts
        await update_saved_button_state(saving_message)

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot Stopped...")

if __name__ == '__main__':
    bot = Bot()
    bot.run()

# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
