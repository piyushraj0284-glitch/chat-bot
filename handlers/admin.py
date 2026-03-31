from aiogram import Router, types
from config import ADMIN_IDS

router = Router()

def extract_user_id(text: str):
    try:
        for line in text.split("\n"):
            if line.startswith("🔒 USER_ID:"):
                return int(line.replace("🔒 USER_ID:", "").strip())
    except:
        return None

@router.message()
async def admin_reply(message: types.Message):
    # Only admins
    if message.from_user.id not in ADMIN_IDS:
        return

    # Must reply
    if not message.reply_to_message:
        return

    reply_msg = message.reply_to_message

    # Extract text or caption
    original_text = reply_msg.text or reply_msg.caption

    if not original_text:
        await message.answer("❌ Cannot detect user")
        return

    user_id = extract_user_id(original_text)

    if not user_id:
        await message.answer("❌ USER_ID not found")
        return

    # ===== SEND REPLY BASED ON TYPE =====

    # TEXT
    if message.text:
        await message.bot.send_message(
            user_id,
            f"💬 Admin:\n{message.text}"
        )

    # PHOTO
    elif message.photo:
        await message.bot.send_photo(
            user_id,
            message.photo[-1].file_id,
            caption=message.caption or ""
        )

    # VIDEO
    elif message.video:
        await message.bot.send_video(
            user_id,
            message.video.file_id,
            caption=message.caption or ""
        )

    # DOCUMENT
    elif message.document:
        await message.bot.send_document(
            user_id,
            message.document.file_id,
            caption=message.caption or ""
        )

    else:
        await message.answer("⚠️ Unsupported reply type")
        return

    await message.answer("✅ Reply sent")
