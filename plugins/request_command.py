from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS

@Client.on_message(filters.command("request") & filters.private)
async def request_command(client: Client, message: Message):
    request_text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    target_channel_id = CHANNEL_ID  # Ensure CHANNEL_ID is set in your config

    if request_text:
        try:
            request_message = await client.send_message(
                chat_id=target_channel_id,
                text=(
                    "<blockquote>📩 New Request Received!</blockquote>\n"
                    f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_name}</a></blockquote>\n"
                    f"<blockquote>🆔 User ID: {user_id}</blockquote>\n"
                    f"<blockquote>📝 Request: {request_text}</blockquote>"
                ),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}_{request_text}")]]
                )
            )
            await message.reply(
                "<blockquote>🎉 Your request has been successfully sent!</blockquote>\n"
                "<blockquote>🔔 Please wait for admin approval.</blockquote>"
            )
        except Exception as e:
            await message.reply(
                f"<blockquote>❌ Failed to send the request.</blockquote>\n"
                f"<blockquote>⚠️ Error: {e}</blockquote>"
            )
    else:
        await message.reply(
            "<blockquote>❗️ Please provide the request text after the command.</blockquote>\n"
            "<blockquote>Example: /request Add XYZ file</blockquote>"
        )


@Client.on_callback_query(filters.regex(r"^accept_\d+_.+$"))
async def accept_request(client: Client, callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    user_id = int(data[1])
    request_text = data[2]
    
    if callback_query.from_user.id in ADMINS:
        admin_name = callback_query.from_user.first_name
        
        # Edit the original message to show request accepted
        new_text = (
            "<blockquote>✅ Request Accepted!</blockquote>\n"
            f"<blockquote>📩 Request: {request_text}</blockquote>\n"
            f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
            f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
        )
        
        try:
            # Edit the original message with updated text and button
            await callback_query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✅ Accepted ✓", callback_data="none")]]
                )
            )
            await callback_query.answer("🎉 Request successfully accepted.")
        except Exception as e:
            await callback_query.answer(
                f"<blockquote>❌ Failed to update the message.</blockquote>\n"
                f"<blockquote>⚠️ Error: {e}</blockquote>",
                show_alert=True
            )
    else:
        await callback_query.answer("🚫 <blockquote>You are not authorized to accept requests.</blockquote>", show_alert=True)
