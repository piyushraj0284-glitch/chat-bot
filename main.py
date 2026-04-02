import os
import asyncio
import random
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
    {"session": "acc4", "api_id": get_api_id("API_ID_4"), "api_hash": get_api_hash("API_HASH_4")},
    {"session": "acc5", "api_id": get_api_id("API_ID_5"), "api_hash": get_api_hash("API_HASH_5")},
]

# ✅ Your message variations
MESSAGES = [
    "Refer to refer dm me on my bio bot link. I have 4 account",
    "Dm me on my bio chat bot. You will get link in my bio",
    "Refer to refer dm me on my bio bot link. I have 4 account",
    "There is bot where you have to do 3 refers then you will get Netflix premium account. DM to get link 🔗",
    "Username to number chahiye to dm karo. Unlimited search 🔍",
]

DELAY_BETWEEN_MSG = 30
LOOP_DELAY = 120

clients = []

# ================= FUNCTIONS =================

async def get_first_3_groups(client):
    groups = []

    async for dialog in client.iter_dialogs():
        try:
            if dialog.is_group:
                groups.append(dialog.entity)

            if len(groups) >= 3:
                break

        except Exception as e:
            print(f"Skip: {e}")

    return groups


async def send_messages(client, groups):
    for group in groups:
        try:
            msg = random.choice(MESSAGES)  # ✅ random message
            await client.send_message(group, msg)

            print(f"✅ Sent to {group.id}: {msg}")

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

            clients.append(client)
            print(f"🚀 Logged in: {acc['session']}")
        except Exception as e:
            print(f"❌ Failed: {acc['session']} → {e}")


async def run_sending():
    for client in clients:
        groups = await get_first_3_groups(client)
        print(f"📊 Using {len(groups)} groups")

        await send_messages(client, groups)


# ================= MAIN =================

async def main():
    await start_clients()

    print("🔥 Running immediately...")
    await run_sending()

    print("⏳ Running every 2 minutes...")

    while True:
        await asyncio.sleep(LOOP_DELAY)
        await run_sending()


if __name__ == "__main__":
    asyncio.run(main())
