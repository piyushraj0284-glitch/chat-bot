from aiogram import Router, types
from db import messages
from config import ADMIN_IDS

router = Router()

@router.message()
async def reply_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    # Must reply
    if not message.reply_to_message:
        return

    reply_msg = message.reply_to_message

    # 🔥 Try match with forwarded message id
    msg = await messages.find_one({
        "admin_msg_id": reply_msg.message_id
    })

    # 🔥 fallback (handles Telegram weird cases)
    if not msg:
        msg = await messages.find_one({
            "admin_msg_id": {
                "$in": [
                    reply_msg.message_id,
                    reply_msg.message_id - 1,
                    reply_msg.message_id + 1
                ]
            }
        })

    if not msg:
        await message.answer("❌ Reply not linked to user")
        return

    user_id = msg["user_id"]

    # Send reply
    await message.bot.send_message(
        user_id,
        f"💬 Admin:\n{message.text}"
    )
