import asyncio
import random
import logging
from telethon import TelegramClient, events
from config import ACCOUNTS, GROUPS, MIN_DELAY, MAX_DELAY

logging.basicConfig(level=logging.INFO)

clients = []

# -------- START CLIENTS --------
async def start_clients():
    for acc in ACCOUNTS:
        try:
            client = TelegramClient(acc["session"], acc["api_id"], acc["api_hash"])
            await client.start()
            clients.append(client)
            logging.info(f"✅ Started {acc['session']}")
        except Exception as e:
            logging.error(f"❌ Failed {acc['session']} -> {e}")

# -------- MESSAGE VARIATION --------
def generate_message(base):
    styles = [
        "🔥 Check this out:",
        "Hey guys 👀",
        "Don’t miss this 👇",
        "Something useful:",
        "Worth checking:"
    ]
    return f"{random.choice(styles)}\n{base}"

# -------- SEND PROMO --------
async def send_promo(text):
    tasks = []

    selected_clients = random.sample(clients, min(len(clients), 3))

    for client in selected_clients:
        for group in GROUPS:
            delay = random.randint(MIN_DELAY, MAX_DELAY)
            msg = generate_message(text)

            async def task(c=client, g=group, m=msg, d=delay):
                await asyncio.sleep(d)
                try:
                    await c.send_message(g, m)
                    logging.info(f"📤 Sent to {g}")
                except Exception as e:
                    logging.error(f"❌ Error: {e}")

            tasks.append(task())

    await asyncio.gather(*tasks)

# -------- COMMAND HANDLER --------
async def setup_controller():
    controller = clients[0]

    @controller.on(events.NewMessage(pattern="/promo"))
    async def handler(event):
        if not event.is_private:
            return

        msg = event.raw_text.replace("/promo", "").strip()

        if not msg:
            await event.reply("❌ Use:\n/promo your message")
            return

        await event.reply("🚀 Sending...")
        await send_promo(msg)
        await event.reply("✅ Done")

    logging.info("🎮 Controller ready")

# -------- MAIN --------
async def main():
    await start_clients()
    await setup_controller()

    logging.info("🔥 Bot running...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
