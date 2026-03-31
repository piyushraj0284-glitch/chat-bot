from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def reply_keyboard(msg_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💬 Reply", callback_data=f"reply:{msg_id}"),
                InlineKeyboardButton(text="📜 History", callback_data=f"history:{msg_id}")
            ]
        ]
    )
