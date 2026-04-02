import os
import asyncio
import random
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

# ❌ Removed acc1
ACCOUNTS = [
    {"session": "acc2", "api_id": get_api_id("API_ID_2"), "api_hash": get_api_hash("API_HASH_2")},
    {"session": "acc3", "api_id": get_api_id("API_ID_3"), "api_hash": get_api_hash("API_HASH_3")},
    {"session": "acc4", "api_id": get_api_id("API_ID_4"), "api_hash": get_api_hash("API_HASH_4")},
    {"session": "acc5", "api_id": get_api_id("API_ID_5"), "api_hash": get_api_hash("API_HASH_5")},
]

MESSAGES = [
    "Refer to refer dm me on my bio bot link. I have 4 account",
    "Dm me on my bio chat bot. You will get link in my bio",
    "There is bot where you have to do 3 refers then you will get Netflix premium account. DM to get link 🔗",
    "Username to number chahiye to dm karo. Unlimited search 🔍",
]

DELAY_BETWEEN_MSG = 60         # ✅ 1 minute
LOOP_DELAY = 120               # 2 minutes
BLOCK_TIME = 25 * 60 * 60      # 25 hours

clients = []
blocked_accounts = {}  # track blocked accounts

# ================= FUNCTIONS =================

async def get_first_group(client):
    async for dialog in client.iter_dialogs():
        try:
            if dialog.is_group:
                return [dialog.entity]
        except Exception as e:
            print(f"Skip: {e}")
    return []


async def send_messages(client, groups, acc_name):
    for group in groups:
        try:
            msg = random.choice(MESSAGES)
            await client.send_message(group, msg)

            print(f"✅ [{acc_name}] Sent to {group.id}")

            await asyncio.sleep(DELAY_BETWEEN_MSG)

        except FloodWaitError as e:
            print(f"⏳ [{acc_name}] Flood wait {e.seconds}s")
            await asyncio.sleep(e.seconds)

        except Exception as e:
            print(f"❌ [{acc_name}] Error → blocking for 25h: {e}")

            # ⛔ block account
            blocked_accounts[acc_name] = time.time()
            return


async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()

            clients.append((acc["session"], client))
            print(f"🚀 Logged in: {acc['session']}")

        except Exception as e:
            print(f"❌ Failed: {acc['session']} → {e}")


async def run_sending():
    for acc_name, client in clients:

        # ⛔ Check block status
        if acc_name in blocked_accounts:
            elapsed = time.time() - blocked_accounts[acc_name]

            if elapsed < BLOCK_TIME:
                print(f"⛔ Skipping {acc_name} (blocked)")
                continue
            else:
                print(f"✅ Unblocking {acc_name}")
                del blocked_accounts[acc_name]

        groups = await get_first_group(client)
        print(f"📊 [{acc_name}] Using {len(groups)} group")

        await send_messages(client, groups, acc_name)


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
