from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS, REQ_CHANNEL_ID
import datetime


@Client.on_message(filters.command("request"))
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

        # Add Accept/Reject buttons
        await request_message.edit_reply_markup(
            InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Accept", callback_data=f"accept_{user_id}_{request_message.id}")],
                [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user_id}_{request_message.id}")]
            ])
        )

        # Notify user
        await message.reply("<blockquote>🎉 Request sent! Await admin approval.</blockquote>")

    except Exception as e:
        await message.reply(f"<blockquote>❌ Request failed.\n⚠️ Error: {e}</blockquote>")


@Client.on_callback_query(filters.regex(r"^(accept|reject)_\d+_\d+$"))
async def handle_request(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("🚫 Unauthorized!", show_alert=True)

    action, user_id, message_id = callback_query.data.split("_")
    user_id, message_id = int(user_id), int(message_id)
    admin_name = callback_query.from_user.first_name

    try:
        request_message = await client.get_messages(REQ_CHANNEL_ID, message_id)
        request_text = request_message.text.split("📝 ")[1].split("</blockquote>")[0]

        if action == "accept":
            # Update the request message to Accepted
            await request_message.edit_text(
                f"<blockquote>✅ Accepted!</blockquote>\n<blockquote>📩 {request_text}</blockquote>\n"
                f"<blockquote>👤 {user_id}</blockquote>\n<blockquote>👑 {admin_name}</blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ Accepted ✓", callback_data="none")]])
            )

            # Forward accepted request to CHANNEL_ID
            await client.send_message(
                CHANNEL_ID,
                f"<blockquote>🎉 Request Forwarded!</blockquote>\n<blockquote>📩 {request_text}</blockquote>\n"
                f"<blockquote>👤 <a href='tg://user?id={user_id}'>{user_id}</a></blockquote>\n<blockquote>👑 {admin_name}</blockquote>"
            )
            # Notify user
            try:
                await client.send_message(user_id, f"<blockquote>✅ Your request was accepted!\n📝 {request_text}\n👑 {admin_name}</blockquote>")
            except Exception:
                pass

            await callback_query.answer("🎉 Request accepted and forwarded!")

        elif action == "reject":
            # Update the request message to Rejected
            await request_message.edit_text(
                f"<blockquote>❌ Rejected!</blockquote>\n<blockquote>📩 {request_text}</blockquote>\n"
                f"<blockquote>👤 {user_id}</blockquote>\n<blockquote>👑 {admin_name}</blockquote>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Rejected ✓", callback_data="none")]])
            )

            # Notify user
            try:
                await client.send_message(user_id, f"<blockquote>❌ Your request was rejected.\n📝 {request_text}\n👑 {admin_name}</blockquote>")
            except Exception:
                pass

            await callback_query.answer("❌ Request rejected!")

    except Exception as e:
        await callback_query.answer(f"❌ Error: {e}", show_alert=True)
