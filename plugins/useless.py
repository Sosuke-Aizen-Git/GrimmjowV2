@Bot.on_message(filters.command('stats'))
async def stats(bot: Bot, message: Message):
    if message.from_user.id in get_admins() + SUDO_USERS:
        sticker = await message.reply_sticker("CAACAgUAAxkBAAEG8_xnzbAQQOfHqMQrzWcOHBvU78EiRgAC_hMAAqiR-FZkMEjJt_CizDYE")

        now = datetime.now()
        delta = now - bot.uptime
        time = get_readable_time(delta.seconds)
        ping = await get_ping(bot)
        total_users_count = len(await full_userbase())

        status_message = (
            f"<pre language='@RedHoodXbot Bot Status:'>"
            f"⏳ Bot Uptime: {time}\n"
            f"⚡ Current Ping: {ping} ms\n"
            f"👤 Total Users: {total_users_count}"
            f"</pre>"
        )

        # Select a random image from the list
        random_image = random.choice(photos)

        # Send the image first
        await message.reply_photo(photo=random_image, caption=status_message)

        # Send a separate message with the effect
        await message.reply_text("✨ Status Updated!", message_effect_id=5046509860389126442)

        await sticker.delete()
    else:
        await message.reply_text("You are not an authorized user!")
