from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS
from urllib.parse import quote, unquote

@Client.on_message(filters.command("request") & filters.private)
async def request_command(client: Client, message: Message):
    request_text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    target_channel_id = CHANNEL_ID  # Ensure CHANNEL_ID is set in your config

    if request_text:  
        try:
            # Encode the request_text to avoid callback errors
            encoded_text = quote(request_text)

            request_message = await client.send_message(
                chat_id=target_channel_id,
                text=f"Request from {user_name} (ID: {user_id}): {request_text}",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Accept", callback_data=f"accept_{user_id}_{encoded_text}")]]
                )
            )
            await message.reply("✅ Your request has been sent successfully.")
        except Exception as e:
            await message.reply(f"❌ Failed to send the request: {e}")
    else:
        await message.reply("⚠️ Please provide a request text after the command.")


@Client.on_callback_query(filters.regex(r"^accept_\d+_.+$"))
async def accept_request(client: Client, callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    user_id = int(data[1])
    
    # Decode the request_text correctly
    request_text = unquote(data[2])

    if callback_query.from_user.id in ADMINS:
        admin_name = callback_query.from_user.first_name

        # Notify the user who made the request
        try:
            await client.send_message(
                chat_id=user_id,
                text=f"🎉 Your request \"{request_text}\" has been accepted by {admin_name}."
            )
            await callback_query.answer("✅ Request accepted and user notified.")

            # Edit the original message to show the request was accepted
            new_text = f"✅ {request_text} requested by {user_id}'s request accepted by {admin_name}."
            await callback_query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Accepted ✓", callback_data="none")]]
                )
            )
        except Exception as e:
            if "chat not found" in str(e).lower() or "user is blocked" in str(e).lower():
                await callback_query.answer("⚠️ User blocked or deleted the chat.", show_alert=True)
            else:
                await callback_query.answer(f"❌ Failed to notify the user: {e}", show_alert=True)
    else:
        await callback_query.answer("⚠️ You are not authorized to accept requests.", show_alert=True)
