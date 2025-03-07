from database.db_handler import get_force_sub_channel, refresh_db_handler
from database.database import add_user, del_user, full_userbase, present_user


@Bot.on_message(filters.command('refresh') & filters.private & filters.user([OWNER_ID] + SUDO_USERS))
@Bot.on_message(filters.command('refresh') & filters.group & filters.user([OWNER_ID] + SUDO_USERS))
async def refresh_command(client, message):
    await refresh_database()
    await refresh_db_handler()
    await refresh_force_sub_channels()
    await message.reply_text("Database and force sub channels have been updated successfully with the latest changes.")
