from aiogram import Router, types
from db import users, messages
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

    # Save message
    msg = await messages.insert_one({
        "user_id": user.id,
        "text": message.text,
        "timestamp": message.date.timestamp()
    })

    # Forward to admin
    for admin in ADMIN_IDS:
        sent = await message.bot.forward_message(
            chat_id=admin,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )

        # 🔥 Save BOTH ids (important)
        await messages.update_one(
            {"_id": msg.inserted_id},
            {
                "$set": {
                    "admin_msg_id": sent.message_id,
                    "user_msg_id": message.message_id
                }
            }
        )
