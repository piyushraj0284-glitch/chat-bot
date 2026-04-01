import asyncio
import random
import logging
from datetime import datetime
from telethon import TelegramClient, events
from config import ACCOUNTS, GROUPS, MIN_DELAY, MAX_DELAY

# ---------------- LOGGING ----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

clients = []
last_sent = {}

# ---------------- START CLIENTS ----------------
async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()
            clients.append(client)
            logging.info(f"✅ Started {acc['session']}")
        except Exception as e:
            logging.error(f"❌ Failed {acc['session']}: {e}")

# ---------------- HUMAN-LIKE VARIATIONS ----------------
def generate_variations(text, n):
    styles = [
        "🔥 Check this out:",
        "Hey guys 👀",
        "Don’t miss this 👇",
        "Something useful:",
        "Worth checking:",
    ]

    variations = []
    for i in range(n):
        prefix = random.choice(styles)
        variations.append(f"{prefix}\n{text}")
    return variations

# ---------------- RATE LIMIT ----------------
def can_send(client_name, group):
    key = f"{client_name}_{group}"
    now = datetime.now()

    if key in last_sent:
        diff = (now - last_sent[key]).seconds
        if diff < 60:  # 1 min cooldown per group/account
            return False

    last_sent[key] = now
    return True

# ---------------- SAFE SEND ----------------
async def safe_send(client, group, message, session_name):
    try:
        if not can_send(session_name, group):
            logging.warning(f"⏳ Rate limit skip {session_name} -> {group}")
            return

        await client.send_message(group, message)
        logging.info(f"📤 {session_name} -> {group}")

    except Exception as e:
        logging.error(f"❌ Error {session_name} -> {group}: {e}")

# ---------------- PROMO ENGINE ----------------
async def send_promo(message):
    if not clients:
        logging.error("No clients available")
        return

    variations = generate_variations(message, len(clients))
    tasks = []

    selected_clients = random.sample(clients, min(len(clients), 3))  # rotate accounts

    for i, client in enumerate(selected_clients):
        session_name = client.session.filename

        assigned_groups = random.sample(GROUPS, min(len(GROUPS), 3))

        for group in assigned_groups:
            delay = random.randint(MIN_DELAY, MAX_DELAY)

            async def task(c=client, g=group, m=variations[i], d=delay, s=session_name):
                await asyncio.sleep(d)
                await safe_send(c, g, m, s)

            tasks.append(task())

    await asyncio.gather(*tasks)

# ---------------- CONTROLLER ----------------
async def setup_controller():
    controller = clients[0]

    @controller.on(events.NewMessage(pattern="/promo"))
    async def handler(event):
        if not event.is_private:
            return

        text = event.raw_text.replace("/promo", "").strip()

        if not text:
            await event.reply("❌ Use:\n/promo your message")
            return

        await event.reply("🚀 Promotion started...")
        await send_promo(text)
        await event.reply("✅ Promotion completed")

    logging.info("🎮 Controller ready")

# ---------------- MAIN ----------------
async def main():
    await start_clients()
    await setup_controller()

    logging.info("🔥 Bot is running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
