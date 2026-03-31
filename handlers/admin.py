from aiogram import Router, types
from config import ADMIN_IDS

router = Router()

@router.message()
async def reply_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    # Must reply to a message
    if not message.reply_to_message:
        return

    text = message.reply_to_message.text

    if not text:
        await message.answer("❌ Cannot detect user")
        return

    # 🔥 Extract user ID from message
    try:
        for line in text.split("\n"):
            if "🆔" in line:
                user_id = int(line.replace("🆔", "").strip())
                break
        else:
            await message.answer("❌ User ID not found")
            return
    except:
        await message.answer("❌ Error reading user ID")
        return

    # Send reply
    await message.bot.send_message(
        user_id,
        f"💬 Admin:\n{message.text}"
    )

    await message.answer("✅ Reply sent")
