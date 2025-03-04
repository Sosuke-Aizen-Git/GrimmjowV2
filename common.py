from pyrogram import Client, __version__
from pyrogram.enums import ParseMode

class Bot(Client):
    def __init__(self, api_hash, api_id, bot_token, tg_bot_workers, logger):
        super().__init__(
            name="Bot",
            api_hash=api_hash,
            api_id=api_id,
            plugins={"root": "plugins"},
            workers=tg_bot_workers,
            bot_token=bot_token
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
