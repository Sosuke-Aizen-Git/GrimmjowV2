from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from plugins.cbb import cb_handler  # Import cb_handler from cbb.py

async def help_command(client, message):
    from bot import Bot  # Lazy import to avoid circular import issue
    buttons = [
        [InlineKeyboardButton("Get Link", callback_data="get_link"), InlineKeyboardButton("Broadcast", callback_data="broadcast"), InlineKeyboardButton("Users", callback_data="users")],
        [InlineKeyboardButton("FSub", callback_data="fsub"), InlineKeyboardButton("Dev", callback_data="dev")],
        [InlineKeyboardButton("Close", callback_data="close")]
    ]
    
    await message.reply_photo(
        photo="https://litter.catbox.moe/21bhag.jpg",  # Replace with the actual URL or file path to your image
        caption="Here are the available commands:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Ensure the cb_handler function is registered with the Bot
def register_handlers(bot):
    bot.add_handler(cb_handler)
    bot.add_handler(help_command)
