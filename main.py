import os
import asyncio
import random
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
    "NETFLIX  PREMIUM ACCOUNT BUY KARNA HAI TO DDMM KARO FAST 🔥.",
    "Username to number chahiye? DM karo, unlimited search available.",
    "NETFLIX ACCOUNT BUY KARNA HAI TO DM KARO🔥 AT JUST 30RS .",
    "NETFLIX ACCOUNT BUY KARNA HAI TO DDMM KARO🔥"
]

AUTO_REPLY = "dm me on this bot to get instant reply @Con_tact_robot"
GROUP_REPLY = "DM me on this bot to get instant reply @Con_tact_robot"

DELAY = 15  # ✅ 15 seconds

clients = []

# ================= AUTO DM REPLY =================

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
            print("💬 DM replied")

        except Exception as e:
            print(f"Reply error: {e}")

# ================= GROUP REPLY =================

def setup_group_reply(client):
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        try:
            if not event.is_group:
                return

            if not event.is_reply:
                return

            replied_msg = await event.get_reply_message()

            if replied_msg.out:
                await asyncio.sleep(2)
                await event.reply(GROUP_REPLY)

                print("💬 Group reply sent")

        except Exception as e:
            print(f"Group reply error: {e}")

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
        print(f"🚫 {acc_name}: banned")

    except Exception as e:
        print(f"❌ {acc_name}: {e}")

# ================= START =================

async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()

            setup_auto_reply(client)
            setup_group_reply(client)

            me = await client.get_me()
            print(f"🚀 {acc['session']} → {me.first_name}")

            clients.append((acc["session"], client))

        except Exception as e:
            print(f"❌ {acc['session']} failed: {e}")

# ================= MAIN =================

async def main():
    await start_clients()

    print("🔥 BOT RUNNING (SEQUENTIAL MODE)")

    while True:
        for acc_name, client in clients:
            await handle_account(acc_name, client)
            await asyncio.sleep(DELAY)  # ✅ delay after each account


if __name__ == "__main__":
    asyncio.run(main())
