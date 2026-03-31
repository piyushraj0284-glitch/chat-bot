@router.message()
async def reply_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not message.reply_to_message:
        return

    admin_msg_id = message.reply_to_message.message_id

    msg = await messages.find_one({"admin_msg_id": admin_msg_id})
    if not msg:
        await message.answer("❌ User not found")
        return

    user_id = msg["user_id"]

    await message.bot.send_message(
        user_id,
        f"💬 Admin:\n{message.text}"
    )

    await message.answer("✅ Reply sent")
