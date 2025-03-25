from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS, REQ_CHANNEL_ID


@Client.on_message(filters.command("request"))
async def request_command(client: Client, message: Message):
    request_text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    target_channel_id = REQ_CHANNEL_ID  # Ensure REQ_CHANNEL_ID is set correctly

    if request_text:
        try:
            # Send the request message and store the message details
            request_message = await client.send_message(
                chat_id=target_channel_id,
                text=(
                    "<blockquote>📩 New Request Received!</blockquote>\n"
                    f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_name}</a></blockquote>\n"
                    f"<blockquote>🆔 User ID: {user_id}</blockquote>\n"
                    f"<blockquote>📝 Request: {request_text}</blockquote>"
                )
            )

            # Edit the message to include the Accept button with correct message ID
            await request_message.edit_text(
                text=request_message.text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}_{request_message.id}")]]
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


@Client.on_callback_query(filters.regex(r"^accept_\d+_\d+$"))
async def accept_request(client: Client, callback_query: CallbackQuery):
    data = callback_query.data.split("_")
    user_id = int(data[1])
    message_id = int(data[2])

    if callback_query.from_user.id in ADMINS:
        admin_name = callback_query.from_user.first_name

        try:
            # Get the original request message
            request_message = await client.get_messages(REQ_CHANNEL_ID, message_id)
            
            # Extract the request text from the original message
            request_text = request_message.text.split("📝 Request: ")[1].split("</blockquote>")[0]

            # Update the original message to show request accepted
            new_text = (
                "<blockquote>✅ Request Accepted!</blockquote>\n"
                f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
                f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
            )

            await request_message.edit_text(
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

            # Notify user that the request has been accepted
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
                pass  # Ignore errors if user has blocked the bot

            await callback_query.answer("🎉 Request successfully accepted and forwarded.")
        except Exception as e:
            await callback_query.answer(
                f"❌ Failed to process the request.\n⚠️ Error: {e}",
                show_alert=True
            )
    else:
        await callback_query.answer("🚫 You are not authorized to accept requests.", show_alert=True)
