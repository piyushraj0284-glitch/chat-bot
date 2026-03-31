from aiogram import Router, types
from config import ADMIN_IDS
from db import users

router = Router()

@router.message()
async def handle_user(message: types.Message):
    # Ignore admin messages
    if message.from_user.id in ADMIN_IDS:
        return

    user = message.from_user

    # Save/update user
    await users.update_one(
        {"user_id": user.id},
        {"$set": {
            "user_id": user.id,
            "name": user.full_name,
            "username": user.username
        }},
        upsert=True
    )

    # Create header (important for reply mapping)
    header = (
        f"🔒 USER_ID:{user.id}\n"
        f"👤 {user.full_name}\n"
        f"🔗 @{user.username if user.username else 'no_username'}\n\n"
    )

    # Handle TEXT
    if message.text:
        for admin in ADMIN_IDS:
            await message.bot.send_message(
                admin,
                header + f"💬 {message.text}"
            )

    # Handle PHOTO
    elif message.photo:
        file_id = message.photo[-1].file_id
        caption = header + (message.caption or "📷 Photo")
        for admin in ADMIN_IDS:
            await message.bot.send_photo(
                admin,
                file_id,
                caption=caption
            )

    # Handle VIDEO
    elif message.video:
        caption = header + (message.caption or "🎥 Video")
        for admin in ADMIN_IDS:
            await message.bot.send_video(
                admin,
                message.video.file_id,
                caption=caption
            )

    # Handle DOCUMENT
    elif message.document:
        caption = header + (message.caption or "📎 File")
        for admin in ADMIN_IDS:
            await message.bot.send_document(
                admin,
                message.document.file_id,
                caption=caption
            )

    else:
        for admin in ADMIN_IDS:
            await message.bot.send_message(
                admin,
                header + "⚠️ Unsupported message type"
            )
