import time
from config import SPAM_LIMIT, SPAM_TIME

user_messages = {}

def is_spam(user_id):
    now = time.time()

    if user_id not in user_messages:
        user_messages[user_id] = []

    user_messages[user_id] = [
        t for t in user_messages[user_id] if now - t < SPAM_TIME
    ]

    user_messages[user_id].append(now)

    return len(user_messages[user_id]) > SPAM_LIMIT
