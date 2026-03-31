from aiogram import Router, types
from config import ADMIN_IDS

router = Router()

@router.message()
async def user_message(message: types.Message):
    # Ignore admin
    if message.from_user.id in ADMIN_IDS:
        return

    user = message.from_user

    text = (
        f"USER_ID:{user.id}\n"
        f"NAME:{user.full_name}\n"
        f"USERNAME:@{user.username if user.username else 'none'}\n\n"
        f"{message.text if message.text else '📎 Media'}"
    )

    for admin in ADMIN_IDS:
        await message.bot.send_message(admin, text)
