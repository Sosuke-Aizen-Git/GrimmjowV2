from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS, REQ_CHANNEL_ID


# Max request length to fit in callback data safely
MAX_REQUEST_LENGTH = 48


def trim_request_text(request_text):
    """Trim request to fit in button safely with ellipsis if too long."""
    if len(request_text) > MAX_REQUEST_LENGTH:
        return request_text[:MAX_REQUEST_LENGTH] + "..."
    return request_text


@Client.on_message(filters.command("request") & filters.private)
async def request_command(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply(
            "<blockquote>❗️ Please provide the request text after the command.</blockquote>\n"
            "<blockquote>Example: /request Add XYZ file</blockquote>"
        )

    request_text = message.text.split(maxsplit=1)[1].strip()
    user_name = message.from_user.first_name
    user_id = message.from_user.id

    # Trim the request text if too long
    trimmed_request = trim_request_text(request_text)

    try:
        # Send the request to REQ_CHANNEL_ID
        request_message = await client.send_message(
            chat_id=REQ_CHANNEL_ID,
            text=(
                "<blockquote>📩 New Request Received!</blockquote>\n"
                f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_name}</a></blockquote>\n"
                f"<blockquote>🆔 User ID: {user_id}</blockquote>\n"
                f"<blockquote>📝 Request: {request_text}</blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Accept", callback_data=f"accept_{user_id}_{trimmed_request}"
                        ),
                        InlineKeyboardButton(
                            "❌ Reject", callback_data=f"reject_{user_id}_{trimmed_request}"
                        ),
                    ]
                ]
            ),
        )

        # Notify the user that the request was sent
        await message.reply(
            "<blockquote>🎉 Your request has been successfully sent!</blockquote>\n"
            "<blockquote>🔔 Please wait for admin approval.</blockquote>"
        )

    except Exception as e:
        await message.reply(
            f"<blockquote>❌ Failed to send the request.</blockquote>\n"
            f"<blockquote>⚠️ Error: {e}</blockquote>"
        )


@Client.on_callback_query(filters.regex(r"^(accept|reject)_\d+_.+$"))
async def handle_request_action(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("🚫 You are not authorized to perform this action.", show_alert=True)

    data = callback_query.data.split("_", 2)
    action = data[0]  # accept or reject
    user_id = int(data[1])
    request_text = data[2]
    admin_name = callback_query.from_user.first_name

    try:
        if action == "accept":
            # Mark the request as accepted
            new_text = (
                "<blockquote>✅ Request Accepted!</blockquote>\n"
                f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
                f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
            )

            # Edit the original message to show accepted status
            await callback_query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✅ Accepted ✓", callback_data="none")]]
                ),
            )

            # Forward accepted request to CHANNEL_ID
            await client.send_message(
                chat_id=CHANNEL_ID,
                text=(
                    "<blockquote>🎉 Request Accepted and Forwarded!</blockquote>\n"
                    f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                    f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_id}</a></blockquote>\n"
                    f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
                ),
            )

            # Notify the user that the request has been accepted
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        "<blockquote>✅ Your request has been accepted!</blockquote>\n"
                        f"<blockquote>📝 Request: {request_text}</blockquote>\n"
                        f"<blockquote>👑 Approved by: {admin_name}</blockquote>"
                    ),
                )
            except Exception:
                pass  # Ignore if the user blocks the bot or deletes the chat

            await callback_query.answer("🎉 Request successfully accepted and forwarded.")

        elif action == "reject":
            # Mark the request as rejected
            new_text = (
                "<blockquote>❌ Request Rejected!</blockquote>\n"
                f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
                f"<blockquote>👑 Rejected by: {admin_name}</blockquote>"
            )

            # Edit the original message to show rejected status
            await callback_query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❌ Rejected ✖️", callback_data="none")]]
                ),
            )

            # Notify the user that the request was rejected
            try:
                await client.send_message(
                    chat_id=user_id,
                    text=(
                        "<blockquote>❌ Your request has been rejected!</blockquote>\n"
                        f"<blockquote>📝 Request: {request_text}</blockquote>\n"
                        f"<blockquote>👑 Rejected by: {admin_name}</blockquote>"
                    ),
                )
            except Exception:
                pass  # Ignore if the user blocks the bot or deletes the chat

            await callback_query.answer("❌ Request has been rejected.")

    except Exception as e:
        await callback_query.answer(f"❌ Failed to process the request.\n⚠️ Error: {e}", show_alert=True)
