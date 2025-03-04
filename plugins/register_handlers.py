from plugins.help import help_command
from plugins.cbb import cb_handler
from bot import Bot

def register_handlers(bot: Bot):
    bot.add_handler(help_command)
    bot.add_handler(cb_handler)
