msg = await messages.insert_one({
    "user_id": message.from_user.id,
    "text": message.text,
    "timestamp": message.date.timestamp()
})

msg_id = str(msg.inserted_id)

for admin in ADMIN_IDS:
    sent = await message.bot.forward_message(
        chat_id=admin,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    # Save mapping
    await messages.update_one(
        {"_id": msg.inserted_id},
        {"$set": {"admin_msg_id": sent.message_id}}
    )
