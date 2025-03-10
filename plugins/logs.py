from pyrogram import Client, filters
from config import OWNER_ID, SUDO_USERS

@Client.on_message(filters.command("logs") & filters.private)
@Client.on_message(filters.command("logs") & filters.group)
async def send_logs(client, message):
    user_id = message.from_user.id
    if user_id == OWNER_ID or user_id in SUDO_USERS:
        try:
            await client.send_document(
                chat_id=message.chat.id,
                document="logs.txt",  # Adjust the path if necessary
                caption="Here are the bot logs."
            )
            await message.reply_text("Logs sent successfully.")
        except FileNotFoundError:
            await message.reply_text("logs.txt file not found. Please check the path.")
        except Exception as e:
            await message.reply_text(f"Failed to send logs: {e}")
    else:
        await message.reply_text("You are not authorized to use this command.")
