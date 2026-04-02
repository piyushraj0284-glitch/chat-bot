import os
import asyncio
import random
import time
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
    {"session": "acc2", "api_id": get_api_id("API_ID_2"), "api_hash": get_api_hash("API_HASH_2")},
    {"session": "acc3", "api_id": get_api_id("API_ID_3"), "api_hash": get_api_hash("API_HASH_3")},
    {"session": "acc4", "api_id": get_api_id("API_ID_4"), "api_hash": get_api_hash("API_HASH_4")},
    {"session": "acc5", "api_id": get_api_id("API_ID_5"), "api_hash": get_api_hash("API_HASH_5")},
]

MESSAGES = [
    "Refer to refer dm me on my bio bot link. I have 4 account",
    "Dm me on my bio chat bot.for refer to refer You will get link in my bio",
    "There is bot where you have to do 3 refers then you will get Netflix premium account. DM to get link 🔗",
    "Username to number chahiye to dm karo. Unlimited search 🔍",
]

AUTO_REPLY = "dm me on this bot to get instant reply @Con_tact_robot"

DELAY_BETWEEN_MSG = 15
BLOCK_TIME = 25 * 60 * 60

clients = []
blocked_accounts = {}
replied_users = set()

# ================= AUTO REPLY =================

def setup_auto_reply(client):
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            if event.is_private:
                user_id = event.sender_id

                if user_id not in replied_users:
                    await event.reply(AUTO_REPLY)
                    replied_users.add(user_id)

                    print(f"💬 Replied once to {user_id}")

        except Exception as e:
            print(f"Reply error: {e}")

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
            blocked_accounts[acc_name] = time.time()
            return


async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()

            setup_auto_reply(client)

            clients.append((acc["session"], client))
            print(f"🚀 Logged in: {acc['session']}")

        except Exception as e:
            print(f"❌ Failed: {acc['session']} → {e}")


async def run_sending():
    for acc_name, client in clients:

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

    print("🔥 Running continuously (cycle-based)...")

    while True:
        await run_sending()   # ✅ next cycle starts after completion


if __name__ == "__main__":
    asyncio.run(main())
