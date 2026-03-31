from aiogram import Router, types
from config import ADMIN_IDS

router = Router()

def extract_user_id(text: str):
    try:
        for line in text.split("\n"):
            if "USER_ID:" in line:
                return int(line.split("USER_ID:")[1].split()[0])
    except:
        return None

@router.message()
async def admin_reply(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.reply_to_message:
        return

    # 🔥 Try both places
    original_text = (
        message.reply_to_message.text
        or message.reply_to_message.caption
        or ""
    )

    # ALSO check replied message inside forwarded/replied
    if not original_text and message.reply_to_message.reply_to_message:
        original_text = message.reply_to_message.reply_to_message.text or ""

    user_id = extract_user_id(original_text)

    if not user_id:
        await message.answer("❌ Reply to correct user message")
        return

    try:
        await message.bot.send_message(
            user_id,
            f"💬 Admin:\n{message.text}"
        )
        await message.answer("✅ Sent")
    except Exception as e:
        await message.answer(f"❌ Error: {e}")
