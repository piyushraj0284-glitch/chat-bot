import os
import asyncio
import random
import schedule
import time
from telethon import TelegramClient
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
]

MIN_DELAY = 30
MAX_DELAY = 120

MESSAGES = [
    "Good morning 🌞",
    "Hello 👋",
    "Good night 🌙"
]

# ================= FUNCTIONS =================

async def get_valid_chats(client):
    chats = []

    async for dialog in client.iter_dialogs():
        try:
            if dialog.is_channel:
                continue

            async for msg in client.iter_messages(dialog.entity, limit=5):
                if msg.out:
                    chats.append(dialog.entity)
                    break

        except Exception as e:
            print(f"Skip: {e}")

    return chats


async def send_messages(client, chats):
    for chat in chats:
        try:
            msg = random.choice(MESSAGES)
            await client.send_message(chat, msg)

            print(f"✅ Sent to {chat.id}: {msg}")

            delay = random.randint(MIN_DELAY, MAX_DELAY)
            await asyncio.sleep(delay)

        except FloodWaitError as e:
            print(f"⏳ Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print(f"❌ Error: {e}")


async def run_all_accounts():
    for acc in ACCOUNTS:
        client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])

        await client.start()
        print(f"🚀 Logged in: {acc['session']}")

        chats = await get_valid_chats(client)
        print(f"📊 {len(chats)} chats found")

        await send_messages(client, chats)

        await client.disconnect()


def job():
    asyncio.run(run_all_accounts())


# ================= SCHEDULER =================

def main():
    schedule.every().day.at("08:00").do(job)
    schedule.every().day.at("22:00").do(job)

    print("⏳ Bot running...")

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
