from aiogram import Router, types
from db import users
from config import ADMIN_IDS

router = Router()

@router.message()
async def handle_user(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        return

    user = message.from_user

    # Save user
    await users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "name": user.full_name,
            "username": user.username
        }},
        upsert=True
    )

    # Create header with hidden ID
    header = (
        f"📩 New Message\n\n"
        f"👤 {user.full_name}\n"
        f"🔗 @{user.username if user.username else 'no_username'}\n"
        f"🆔 {user.id}\n\n"
    )

    # Send to admins
    for admin in ADMIN_IDS:
        await message.bot.send_message(
            admin,
            header + (message.text or "📎 Media message"),
        )
