import os
import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError

# ================= CONFIG =================

DEFAULT_API_ID = 32316600
DEFAULT_API_HASH = "dd2eb107af3f31e35cbfe02dca616d1a"

def get_api_id(key):
    value = os.getenv(key)
    return int(value) if value else DEFAULT_API_ID

def get_api_hash(key):
    value = os.getenv(key)
    return value if value else DEFAULT_API_HASH

ACCOUNTS = [
    {"session": "acc1", "api_id": get_api_id("API_ID_1"), "api_hash": get_api_hash("API_HASH_1")},
    {"session": "acc2", "api_id": get_api_id("API_ID_2"), "api_hash": get_api_hash("API_HASH_2")},
    {"session": "acc3", "api_id": get_api_id("API_ID_3"), "api_hash": get_api_hash("API_HASH_3")},
    {"session": "acc4", "api_id": get_api_id("API_ID_4"), "api_hash": get_api_hash("API_HASH_4")},
    {"session": "acc5", "api_id": get_api_id("API_ID_5"), "api_hash": get_api_hash("API_HASH_5")},
]

MESSAGE = "Hello 👋"
REPLY_MESSAGE = "I have work for you"

DELAY_BETWEEN_MSG = 30   # 30 seconds
LOOP_DELAY = 300         # 5 minutes

clients = []

# ================= AUTO REPLY =================

def setup_auto_reply(client):
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            if event.is_private:
                await event.reply(REPLY_MESSAGE)
                print(f"💬 Replied to {event.sender_id}")
        except Exception as e:
            print(f"Reply error: {e}")

# ================= FUNCTIONS =================

async def get_private_chats(client):
    chats = []
    async for dialog in client.iter_dialogs():
        try:
            if dialog.is_user:
                chats.append(dialog.entity)
        except Exception as e:
            print(f"Skip: {e}")
    return chats


async def send_messages(client, chats):
    for chat in chats:
        try:
            await client.send_message(chat, MESSAGE)
            print(f"✅ Sent to {chat.id}")

            await asyncio.sleep(DELAY_BETWEEN_MSG)

        except FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print(f"❌ Error: {e}")


async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()

            setup_auto_reply(client)

            clients.append(client)
            print(f"🚀 Logged in: {acc['session']}")
        except Exception as e:
            print(f"❌ Failed: {acc['session']} → {e}")


async def run_sending():
    for client in clients:
        chats = await get_private_chats(client)
        print(f"📊 {len(chats)} chats found")

        await send_messages(client, chats)

# ================= MAIN LOOP =================

async def main():
    await start_clients()

    print("🔥 Running immediately...")

    # ✅ Run immediately first
    await run_sending()

    print("⏳ Now running every 5 minutes...")

    # 🔁 Loop every 5 minutes
    while True:
        await asyncio.sleep(LOOP_DELAY)
        await run_sending()


if __name__ == "__main__":
    asyncio.run(main())
