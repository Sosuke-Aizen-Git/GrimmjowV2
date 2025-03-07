from pyrofork.types import InlineKeyboardMarkup, InlineKeyboardButton

# Function to update the button state to "Saved" after restart
async def update_saved_button_state(saving_message):
    if saving_message:
        await saving_message.edit_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton("✅ Saved", callback_data="saved")]])
        )
        saving_message = None
