from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from config import CHANNEL_ID, ADMINS, REQ_CHANNEL_ID
import time

# Cooldown dictionary to store last request timestamps
user_cooldown = {}
COOLDOWN_TIME = 60  # Cooldown time in seconds (1 minute)


@Client.on_message(filters.command("request"))
async def request_command(client: Client, message: Message):
    user_id = message.from_user.id
    if len(message.command) == 1:
        return await message.reply(
            "<blockquote>❗️ Please provide the request text after the command.</blockquote>\n"
            "<blockquote>Example: /request Add XYZ file</blockquote>"
        )

    # Check if the user is an admin (no cooldown for admins)
    if user_id not in ADMINS:
        last_request_time = user_cooldown.get(user_id, 0)
        if time.time() - last_request_time < COOLDOWN_TIME:
            remaining_time = int(COOLDOWN_TIME - (time.time() - last_request_time))
            return await message.reply(
                f"<blockquote>⏳ Please wait {remaining_time} seconds before sending another request.</blockquote>"
            )
        # Update last request time for non-admin users
        user_cooldown[user_id] = time.time()

    request_text = message.text.split(maxsplit=1)[1].strip()
    user_name = message.from_user.first_name
    chat_type = "Group" if message.chat.type in ["group", "supergroup"] else "Private"

    try:
        # Send request to REQ_CHANNEL_ID
        request_message = await client.send_message(
            chat_id=REQ_CHANNEL_ID,
            text=(
                "<blockquote>📩 New Request Received!</blockquote>\n"
                f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_name}</a></blockquote>\n"
                f"<blockquote>🆔 User ID: {user_id}</blockquote>\n"
                f"<blockquote>📝 Request: {request_text}</blockquote>\n"
                f"<blockquote>💬 Source: {chat_type}</blockquote>"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "✅ Accept", callback_data=f"accept|{user_id}|{request_text}"
                        ),
                        InlineKeyboardButton(
                            "❌ Reject", callback_data=f"reject|{user_id}|{request_text}")
                    ]
                ]
            ),
        )

        # Notify the user that the request was sent
        await message.reply(
            "<blockquote>✅ Request sent successfully!</blockquote>\n"
            "<blockquote>📬 Check your DM for updates.</blockquote>"
        )

    except Exception as e:
        await message.reply(
            f"<blockquote>❌ Failed to send the request.</blockquote>\n"
            f"<blockquote>⚠️ Error: {e}</blockquote>"
        )


@Client.on_callback_query(filters.regex(r"^(accept|reject)\|(\d+)\|(.+)$"))
async def handle_request_action(client: Client, callback_query: CallbackQuery):
    if callback_query.from_user.id not in ADMINS:
        return await callback_query.answer("🚫 You are not authorized to perform this action.", show_alert=True)

    action, user_id, request_text = callback_query.data.split("|", 2)
    user_id = int(user_id)
    admin_name = callback_query.from_user.first_name

    try:
        if action == "accept":
            # Mark request as accepted
            new_text = (
                "<blockquote>✅ Request Accepted!</blockquote>\n"
                f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
                f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
            )

            # Update the original message to show accepted status
            await callback_query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("✅ Accepted ✓", callback_data="none")]]
                ),
            )

            # Forward accepted request to CHANNEL_ID
            # Currently this function is disabled, if you want to use this function to then remove the three quots
            '''await client.send_message(
                chat_id=CHANNEL_ID,
                text=(
                    "<blockquote>🎉 Request Accepted and Forwarded!</blockquote>\n"
                    f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                    f"<blockquote>👤 User: <a href='tg://user?id={user_id}'>{user_id}</a></blockquote>\n"
                    f"<blockquote>👑 Accepted by: {admin_name}</blockquote>"
                ),
            )'''

            # Notify the user about acceptance
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
                pass  # Ignore if the user blocks the bot

            await callback_query.answer("🎉 Request successfully accepted and forwarded.")

        elif action == "reject":
            # Mark request as rejected
            new_text = (
                "<blockquote>❌ Request Rejected!</blockquote>\n"
                f"<blockquote>📩 Request: {request_text}</blockquote>\n"
                f"<blockquote>👤 User ID: {user_id}</blockquote>\n"
                f"<blockquote>👑 Rejected by: {admin_name}</blockquote>"
            )

            # Update the original message to show rejected status
            await callback_query.message.edit_text(
                text=new_text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("❌ Rejected ✖️", callback_data="none")]]
                ),
            )

            # Notify the user about rejection
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
                pass  # Ignore if the user blocks the bot

            await callback_query.answer("❌ Request has been rejected.")

    except Exception as e:
        await callback_query.answer(f"❌ Failed to process the request.\n⚠️ Error: {e}", show_alert=True)
