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
    {"session": "acc1", "api_id": get_api_id("API_ID_1"), "api_hash": get_api_hash("API_HASH_1")},
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

AUTO_REPLY = "dm me on this bot to get instant reply @Con_tact_robot"

BLOCK_TIME = 5 * 60

clients = []
blocked_accounts = {}

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

            await asyncio.sleep(random.randint(1, 3))

            await event.reply(AUTO_REPLY)
            print(f"💬 [{client.session.filename}] Replied")

        except Exception as e:
            print(f"Reply error: {e}")

# ================= GROUP LOGIC =================

async def get_first_group(client):
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            return dialog.entity
    return None

# ================= ACCOUNT TASK =================

async def handle_account(acc_name, client):

    # ⛔ block check
    if acc_name in blocked_accounts:
        elapsed = time.time() - blocked_accounts[acc_name]

        if elapsed < BLOCK_TIME:
            print(f"⛔ {acc_name} blocked")
            return
        else:
            print(f"✅ {acc_name} unblocked")
            del blocked_accounts[acc_name]

    group = await get_first_group(client)

    if not group:
        print(f"⚠️ {acc_name} no group found")
        return

    try:
        msg = random.choice(MESSAGES)
        await client.send_message(group, msg)

        print(f"✅ [{acc_name}] → {group.id}")

        await asyncio.sleep(random.randint(30, 60))

    except FloodWaitError as e:
        print(f"⏳ [{acc_name}] Flood wait {e.seconds}")
        await asyncio.sleep(e.seconds)

    except Exception as e:
        print(f"❌ [{acc_name}] blocked: {e}")
        blocked_accounts[acc_name] = time.time()

# ================= START =================

async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()

            setup_auto_reply(client)

            clients.append((acc["session"], client))
            print(f"🚀 {acc['session']} started")

        except Exception as e:
            print(f"❌ {acc['session']} failed: {e}")

# ================= MAIN =================

async def main():
    await start_clients()

    print("🔥 ULTRA SAFE PARALLEL (FIXED GROUP) RUNNING...")

    while True:
        tasks = []

        for acc_name, client in clients:
            tasks.append(handle_account(acc_name, client))

        await asyncio.gather(*tasks)

        # 🔁 random cycle delay
        await asyncio.sleep(random.randint(60, 120))


if __name__ == "__main__":
    asyncio.run(main())
