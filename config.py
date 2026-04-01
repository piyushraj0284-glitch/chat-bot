import os

def get_api_id(key):
    value = os.getenv(key)
    if value is None:
        return 32316600  # 👈 PUT YOUR REAL API ID HERE
    return int(value)

def get_api_hash(key):
    value = os.getenv(key)
    if value is None:
        return "dd2eb107af3f31e35cbfe02dca616d1a"  # 👈 PUT YOUR REAL HASH HERE
    return value

ACCOUNTS = [
    {"session": "acc1", "api_id": get_api_id("API_ID_1"), "api_hash": get_api_hash("API_HASH_1")},
    {"session": "acc2", "api_id": get_api_id("API_ID_2"), "api_hash": get_api_hash("API_HASH_2")},
    {"session": "acc3", "api_id": get_api_id("API_ID_3"), "api_hash": get_api_hash("API_HASH_3")},
    {"session": "acc4", "api_id": get_api_id("API_ID_4"), "api_hash": get_api_hash("API_HASH_4")},
    {"session": "acc5", "api_id": get_api_id("API_ID_5"), "api_hash": get_api_hash("API_HASH_5")},
]

GROUPS = [
    -1001234567890,
    -1009876543210,
]

MIN_DELAY = 30
MAX_DELAY = 120
