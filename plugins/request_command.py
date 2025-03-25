import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS, REQ_CHANNEL_ID


def encode_request(text):
    """Encode request text to base64 (URL-safe)"""
    return base64.urlsafe_b64encode(text.encode()).decode()


def decode_request(encoded_text):
    """Decode base64-encoded request text"""
    return base64.urlsafe_b64decode(encoded_text.encode()).decode()


@Client.on_message(filters.command("request") & filters.private)
async def request_command(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply(
            "<blockquote>❗️ Please provide the request text after the command.</blockquote>\n"
            "<blockquote>Example: /request Add XYZ file</blockquote>"
        )

    request_text = message.text.split(maxsplit=1)[1]
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    # Encode the request text for safe storage in button
    encoded_request = encode_request(request_text)

    try:
        # Send request message with Accept button (encoded request in button)
        request_message = await client.send_message(
            chat_id=REQ_CHANNEL_ID,
            text=(
                "<blockquote>📩 New Request Received!</blockquote>\n"
                f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_name}</a></blockquote>\n"
                f"<blockquote>🆔 User ID: {user_id}</blockquote>\n"
                f"<blockquote>📝 Request: {request_text}</blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}_{encoded_request}")]]
            )
        )

        # Notify the user
        await message.reply(
            "<blockquote>🎉 Your request has been successfully sent!</blockquote>\n"
            "<blockquote>🔔 Please wait for admin approval.</blockquote>"
        )

    except Exception as e:
        await message.reply(
            f"<blockquote>❌ Failed to send the request.</blockquote>\n"
            f"<blockquote>⚠️ Error: {e}</blockquote>"
        )


@Client.on_callback_query(filters.regex(r"^accept_\d+_.+$"))
async def accept_request(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("🚫 You are not authorized to accept requests.", show_alert=True)

    data = callback_query.data.split("_", 2)
    user_id = int(data[1])
    encoded_request = data[2]
    admin_name = callback_query.from_user.first_name

    try:
        # Decode request text safely
        try:
            request_text = decode_request(encoded_request)
        except Exception:
            return await callback_query.answer("❌ Error decoding request. Please try again.", show_alert=True)

        # Edit original request message to show as Accepted
        new_text = (
            "<blockquote>✅ Request Accepted!</blockquote>\n"
            f"<blockquote>📩 Request: {request_text}</blockquote>\n"
            f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
            f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
        )

        # Edit button to show Accepted
        await callback_query.message.edit_text(
            text=new_text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✅ Accepted ✓", callback_data="none")]]
            )
        )

        # Forward accepted request to CHANNEL_ID
        await client.send_message(
            chat_id=CHANNEL_ID,
            text=(
                "<blockquote>🎉 Request Accepted and Forwarded!</blockquote>\n"
                f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_id}</a></blockquote>\n"
                f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
            )
        )

        # Notify the user about the accepted request
        try:
            await client.send_message(
                chat_id=user_id,
                text=(
                    "<blockquote>✅ Your request has been accepted!</blockquote>\n"
                    f"<blockquote>📝 Request: {request_text}</blockquote>\n"
                    f"<blockquote>👑 Approved by: {admin_name}</blockquote>"
                )
            )
        except Exception:
            pass  # Ignore errors if user blocked the bot or deleted the chat

        await callback_query.answer("🎉 Request successfully accepted and forwarded.")

    except Exception as e:
        await callback_query.answer(f"❌ Failed to process the request.\n⚠️ Error: {e}", show_alert=True)
