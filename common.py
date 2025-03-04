from pyrogram import Client, __version__
from pyrogram.enums import ParseMode
from config.py import BOT_TOKEN, API_ID, API_HASH, TG_BOT_WORKERS
class Bot(Client):
    def __init__(self, api_hash, api_id, bot_token, tg_bot_workers, logger):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = logger

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.set_parse_mode(ParseMode.HTML)
        self.username = usr_bot_me.username

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot Stopped...")
