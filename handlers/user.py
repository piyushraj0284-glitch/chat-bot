from aiogram import Router, types
from db import users, messages
from keyboards.inline import reply_keyboard
from config import ADMIN_IDS
from services.spam import is_spam

router = Router()

@router.message()
async def handle_user(message: types.Message):
    if message.from_user.id in ADMIN_IDS:
        return

    user_id = message.from_user.id

    # Anti-spam
    if is_spam(user_id):
        await message.answer("🚫 Too many messages. Slow down.")
        return

    # Save user
    await users.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

    # Save message
    msg = await messages.insert_one({
        "user_id": user_id,
        "text": message.text,
        "timestamp": message.date.timestamp()
    })

    msg_id = str(msg.inserted_id)

    # Send to admins
    for admin in ADMIN_IDS:
        await message.bot.send_message(
            admin,
            f"📩 New Message\nUser: {user_id}\n\n{message.text}",
            reply_markup=reply_keyboard(msg_id)
        )
