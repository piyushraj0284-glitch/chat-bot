import os
import asyncio
import random
import time
from telethon import TelegramClient, events
from telethon.errors import FloodWaitError, UserBannedInChannelError

# ================= CONFIG =================

DEFAULT_API_ID = 32316600
DEFAULT_API_HASH = "dd2eb107af3f31e35cbfe02dca616d1a"

def get_api_id(key):
    return int(os.getenv(key) or DEFAULT_API_ID)

def get_api_hash(key):
    return os.getenv(key) or DEFAULT_API_HASH

ACCOUNTS = [
    {"session": "acc1", "api_id": get_api_id("API_ID_1"), "api_hash": get_api_hash("API_HASH_1")},
    {"session": "acc2", "api_id": get_api_id("API_ID_2"), "api_hash": get_api_hash("API_HASH_2")},
    {"session": "acc3", "api_id": get_api_id("API_ID_3"), "api_hash": get_api_hash("API_HASH_3")},
    {"session": "acc4", "api_id": get_api_id("API_ID_4"), "api_hash": get_api_hash("API_HASH_4")},
    {"session": "acc5", "api_id": get_api_id("API_ID_5"), "api_hash": get_api_hash("API_HASH_5")},
]

MESSAGES = [
    "Hello 👋",
    "Hi 🙂",
    "Hey there!",
]

AUTO_REPLY = "Reply received 👍"

DELAY = 5  # ⚡ fast but not zero (important)

clients = []

# ================= AUTO REPLY =================

def setup_auto_reply(client):
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            if not event.is_private:
                return

            if event.out:
                return

            sender = await event.get_sender()
            if sender.bot:
                return

            await event.reply(AUTO_REPLY)

        except Exception as e:
            print(f"Reply error: {e}")

# ================= FUNCTIONS =================

async def get_first_group(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            return dialog.entity
    return None


async def handle_account(acc_name, client):
    try:
        group = await get_first_group(client)

        if not group:
            print(f"⚠️ {acc_name}: No group")
            return

        msg = random.choice(MESSAGES)
        await client.send_message(group, msg)

        print(f"✅ {acc_name}: sent")

    except FloodWaitError as e:
        print(f"⏳ {acc_name}: Flood wait {e.seconds}s")
        await asyncio.sleep(e.seconds)

    except UserBannedInChannelError:
        print(f"🚫 {acc_name}: banned in group")

    except Exception as e:
        print(f"❌ {acc_name}: {e}")

    await asyncio.sleep(DELAY)


async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()

            setup_auto_reply(client)

            me = await client.get_me()
            print(f"🚀 {acc['session']} → {me.first_name}")

            clients.append((acc["session"], client))

        except Exception as e:
            print(f"❌ {acc['session']} failed: {e}")


# ================= MAIN =================

async def main():
    await start_clients()

    print("🔥 FAST SAFE SYSTEM RUNNING")

    while True:
        tasks = [handle_account(name, client) for name, client in clients]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
