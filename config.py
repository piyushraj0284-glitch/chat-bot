import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS").split(",")]

SPAM_LIMIT = 5  # messages
SPAM_TIME = 10  # seconds
