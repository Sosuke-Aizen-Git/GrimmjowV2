from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS, REQ_CHANNEL_ID
import datetime

# Dictionary to store request data temporarily
requests_data = {}


@Client.on_message(filters.command("request") & filters.private)
async def request_command(client: Client, message: Message):
    if len(message.command) == 1:
        return await message.reply("<blockquote>❗️ Provide request text.\nExample: /request Add XYZ file</blockquote>")

    request_text = message.text.split(maxsplit=1)[1]
    user_id, user_name = message.from_user.id, message.from_user.first_name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        # Send request to REQ_CHANNEL_ID with Accept/Reject buttons
        request_message = await client.send_message(
            REQ_CHANNEL_ID,
            f"<blockquote>📩 New Request!</blockquote>\n"
            f"<blockquote>👤 <a href='tg://user?id={user_id}'>{user_name}</a></blockquote>\n"
            f"<blockquote>🆔 {user_id}</blockquote>\n"
            f"<blockquote>📝 {request_text}</blockquote>\n"
            f"<blockquote>⏰ Time: {timestamp}</blockquote>"
        )

        # Store request details in dictionary
        requests_data[request_message.id] = {
            "user_id": user_id,
            "request_text": request_text,
            "message_id": request_message.id
        }

        # Add Accept/Reject buttons with correct callback data
        await request_message.edit_reply_markup(
            InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Accept", callback_data=f"action:accept:{request_message.id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"action:reject:{request_message.id}")
                ]
            ])
        )

        # Notify user
        await message.reply("<blockquote>🎉 Request sent! Await admin approval.</blockquote>")

    except Exception as e:
        await message.reply(f"<blockquote>❌ Request failed.\n⚠️ Error: {e}</blockquote>")


@Client.on_callback_query(filters.regex(r"^action:(accept|reject):(\d+)$"))
async def handle_request(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("🚫 Unauthorized!", show_alert=True)

    # Extract action and request_id correctly
    data_parts = callback_query.data.split(":")
    action, request_id = data_parts[1], int(data_parts[2])
    admin_name = callback_query.from_user.first_name

    # Fetch request details from the dictionary
    request_info = requests_data.pop(request_id, None)

    # Handle case if request data is not found
    if not request_info:
        # If request is missing, update the original message
        try:
            expired_message = await client.get_messages(REQ_CHANNEL_ID, request_id)
            await expired_message.edit_text(
                "<blockquote>⚠️ Request Expired or Already Processed!</blockquote>\n"
                "<blockquote>❌ Action not possible anymore.</blockquote>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⚠️ Expired ✓", callback_data="none")]]
                )
            )
        except Exception:
            pass

        # Alert admin that the request is invalid or expired
        return await callback_query.answer("⚠️ Request expired or already processed!", show_alert=True)

    user_id = request_info["user_id"]
    request_text = request_info["request_text"]
    message_id = request_info["message_id"]

    try:
        # Get the original request message from REQ_CHANNEL_ID
        request_message = await client.get_messages(REQ_CHANNEL_ID, message_id)

        if action == "accept":
            # Update the request message to Accepted
            await request_message.edit_text(
                f"<blockquote>✅ Accepted!</blockquote>\n"
                f"<blockquote>📩 {request_text}</blockquote>\n"
                f"<blockquote>👤 {user_id}</blockquote>\n"
                f"<blockquote>👑 {admin_name}</blockquote>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✅ Accepted ✓", callback_data="none")]]
                )
            )

            # Forward accepted request to CHANNEL_ID
            await client.send_message(
                CHANNEL_ID,
                f"<blockquote>🎉 Request Forwarded!</blockquote>\n"
                f"<blockquote>📩 {request_text}</blockquote>\n"
                f"<blockquote>👤 <a href='tg://user?id={user_id}'>{user_id}</a></blockquote>\n"
                f"<blockquote>👑 {admin_name}</blockquote>"
            )

            # Notify user about request acceptance
            try:
                await client.send_message(
                    user_id,
                    f"<blockquote>✅ Your request was accepted!</blockquote>\n"
                    f"<blockquote>📝 {request_text}</blockquote>\n"
                    f"<blockquote>👑 Approved by: {admin_name}</blockquote>"
                )
            except Exception:
                pass  # Ignore errors if the user blocked the bot or deleted the chat

            await callback_query.answer("🎉 Request accepted and forwarded!")

        elif action == "reject":
            # Update the request message to Rejected
            await request_message.edit_text(
                f"<blockquote>❌ Rejected!</blockquote>\n"
                f"<blockquote>📩 {request_text}</blockquote>\n"
                f"<blockquote>👤 {user_id}</blockquote>\n"
                f"<blockquote>👑 {admin_name}</blockquote>",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❌ Rejected ✓", callback_data="none")]]
                )
            )

            # Notify user about request rejection
            try:
                await client.send_message(
                    user_id,
                    f"<blockquote>❌ Your request was rejected.</blockquote>\n"
                    f"<blockquote>📝 {request_text}</blockquote>\n"
                    f"<blockquote>👑 Rejected by: {admin_name}</blockquote>"
                )
            except Exception:
                pass

            await callback_query.answer("❌ Request rejected!")

    except Exception as e:
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)
