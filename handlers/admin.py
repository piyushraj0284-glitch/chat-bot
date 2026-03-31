from aiogram import Router, types, F
from db import messages
from config import ADMIN_IDS
from bson import ObjectId

router = Router()

reply_state = {}

# Reply button
@router.callback_query(F.data.startswith("reply:"))
async def reply_start(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    msg_id = callback.data.split(":")[1]
    reply_state[callback.from_user.id] = msg_id

    await callback.message.answer("✏️ Send your reply")

# History button
@router.callback_query(F.data.startswith("history:"))
async def show_history(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    msg_id = callback.data.split(":")[1]
    msg = await messages.find_one({"_id": ObjectId(msg_id)})

    if not msg:
        return

    user_id = msg["user_id"]

    history = []
    async for m in messages.find({"user_id": user_id}).sort("timestamp", -1).limit(5):
        history.append(m["text"])

    await callback.message.answer("📜 Last messages:\n\n" + "\n\n".join(history))

# Send reply
@router.message()
async def send_reply(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    msg_id = reply_state.get(message.from_user.id)
    if not msg_id:
        return

    msg = await messages.find_one({"_id": ObjectId(msg_id)})
    if not msg:
        await message.answer("❌ Message not found")
        return

    user_id = msg["user_id"]

    await message.bot.send_message(
        user_id,
        f"💬 Admin:\n{message.text}"
    )

    await message.answer("✅ Reply sent")
    reply_state.pop(message.from_user.id, None)


# Broadcast
@router.message(F.text.startswith("/broadcast"))
async def broadcast(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    text = message.text.replace("/broadcast ", "")

    from db import users

    count = 0
    async for user in users.find():
        try:
            await message.bot.send_message(user["user_id"], text)
            count += 1
        except:
            pass

    await message.answer(f"✅ Sent to {count} users")
