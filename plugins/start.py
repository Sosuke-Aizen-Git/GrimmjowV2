successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1
        
        status = f"""<b><u>Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""
        
        return await pls_wait.edit(status)

    else:
        msg = await message.reply(f"Use This Command As A Reply To Any Telegram Message With Out Any Spaces.")
        await asyncio.sleep(8)
        await msg.delete()


@Client.on_message(filters.command("fsubs") & filters.user([OWNER_ID] + ADMINS))
async def force_subs(client, message):
    channels = [FORCE_SUB_CHANNEL, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4]
    
    buttons = []
    for channel in channels:
        if channel and str(channel).startswith("-100"):  # Ensure it's a valid channel ID
            try:
                chat = await client.get_chat(channel)  # Fetch channel details
                invite_link = await client.create_chat_invite_link(channel)
                buttons.append([InlineKeyboardButton(chat.title, url=invite_link.invite_link)])  # Use channel name
            except Exception as e:
                print(f"Error generating invite link for {channel}: {e}")
    
    if not buttons:
        return await message.reply_text("No valid force subscription channels found!")

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text("Here is the list of force subscription channels:", reply_markup=reply_markup)




# Function to handle file deletion
async def delete_files(messages, client, k):
    await asyncio.sleep(FILE_AUTO_DELETE)  # Wait for the duration specified in config.py
    for msg in messages:
        try:
            await client.delete_messages(chat_id=msg.chat.id, message_ids=[msg.id])
        except Exception as e:
            print(f"The attempt to delete the media {msg.id} was unsuccessful: {e}")
    # await client.send_message(messages[0].chat.id, "Your Video / File Is Successfully Deleted ✅")
    await k.edit_text("Your Video / File Is Successfully Deleted ✅")


@Client.on_message(filters.command("admins") & filters.user([OWNER_ID] + ADMINS))
async def list_admins(client, message):
    unique_admins = list(set(ADMINS))  # Remove duplicate IDs
    admins_list = []
    
    for index, admin_id in enumerate(unique_admins, start=1):
        try:
            user = await client.get_users(admin_id)  # Fetch user details
            admin_name = f"[{user.first_name}]( tg://openmessage?user_id={admin_id} )"
        except Exception:
            admin_name = f"{admin_id} (Bot not started)"  # If user data not found
        
        admins_list.append(f"{index}. {admin_name} ({admin_id})")
    
    admin_text = "👮‍♂️ Here is the list of bot admins:\n\n" + "\n".join(admins_list)
    await message.reply_text(admin_text, disable_web_page_preview=True)



@Client.on_message(filters.private & filters.command("fpbroadcast") & filters.user([OWNER_ID] + ADMINS))
async def forward_broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("❌ Use this command as a reply to the message you want to forward.")

    query = await full_userbase()
    forward_msg = message.reply_to_message
    total, successful, blocked, deleted, unsuccessful = len(query), 0, 0, 0, 0

    pls_wait = await message.reply("<i>Forwarding message to all users... This may take some time.</i>")

    for chat_id in query:
        try:
            sent_msg = await forward_msg.forward(chat_id)
            successful += 1
# Try to pin the message
            try:
                await client.pin_chat_message(chat_id, sent_msg.id)
            except ChatAdminRequired:
                print(f"Cannot pin message in {chat_id}, bot is not an admin.")

        except FloodWait as e:
            await asyncio.sleep(e.x)
            sent_msg = await forward_msg.forward(chat_id)
            successful += 1
            try:
                await client.pin_chat_message(chat_id, sent_msg.id)
            except ChatAdminRequired:
                print(f"Cannot pin message in {chat_id}, bot is not an admin.")

        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except Exception as e:
            print(f"Error sending to {chat_id}: {e}")
            unsuccessful += 1
            continue

    status = f"""<b><u>✅ Forward Broadcast Completed</u></b>

<b>Total Users :</b> <code>{total}</code>
<b>Successful :</b> <code>{successful}</code>
<b>Blocked Users :</b> <code>{blocked}</code>
<b>Deleted Accounts :</b> <code>{deleted}</code>
<b>Unsuccessful :</b> <code>{unsuccessful}</code>"""

    return await pls_wait.edit(status)


# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Backup Channel @JishuBotz
# Developer @JishuDeveloper
