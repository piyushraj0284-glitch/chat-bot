from aiogram import Router, types
from config import ADMIN_IDS

router = Router()

def extract_user_id(text: str):
    for line in text.split("\n"):
        if "USER_ID:" in line:
            try:
                return int(line.replace("🔒 USER_ID:", "").replace("USER_ID:", "").strip())
            except:
                return None
    return None

@router.message()
async def admin_reply(message: types.Message):
    print("🔥 ADMIN HANDLER TRIGGERED")

    if message.from_user.id not in ADMIN_IDS:
        print("❌ Not admin")
        return

    if not message.reply_to_message:
        print("❌ Not a reply")
        return

    reply_msg = message.reply_to_message

    original_text = reply_msg.text or reply_msg.caption

    print("📩 ORIGINAL MESSAGE:", original_text)

    if not original_text:
        await message.answer("❌ No original message")
        return

    user_id = extract_user_id(original_text)

    print("🎯 EXTRACTED USER ID:", user_id)

    if not user_id:
        await message.answer("❌ USER_ID not found")
        return

    try:
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
            await message.answer("⚠️ Unsupported type")
            return

        await message.answer("✅ Reply sent")
        print("✅ SENT SUCCESSFULLY")

    except Exception as e:
        print("❌ ERROR:", e)
        await message.answer("❌ Failed to send")
