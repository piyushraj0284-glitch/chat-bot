from aiogram import Router, types
from config import ADMIN_IDS

router = Router()

@router.message()
async def admin_reply(message: types.Message):
    # Only admin
    if message.from_user.id not in ADMIN_IDS:
        return

    # Must reply
    if not message.reply_to_message:
        return

    original = message.reply_to_message.text

    if not original:
        await message.answer("❌ Cannot detect user")
        return

    # Extract user_id
    try:
        first_line = original.split("\n")[0]
        user_id = int(first_line.replace("USER_ID:", "").strip())
    except:
        await message.answer("❌ Invalid reply")
        return

    try:
        # Send reply
        if message.text:
            await message.bot.send_message(
                user_id,
                f"💬 Admin:\n{message.text}"
            )
        else:
            await message.answer("⚠️ Only text supported in this version")
            return

        await message.answer("✅ Sent")

    except Exception as e:
        await message.answer(f"❌ Error: {e}")
