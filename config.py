import os

ACCOUNTS = [
    {"session": "acc1", "api_id": int(os.getenv("API_ID_1")), "api_hash": os.getenv("API_HASH_1")},
    {"session": "acc2", "api_id": int(os.getenv("API_ID_2")), "api_hash": os.getenv("API_HASH_2")},
    {"session": "acc3", "api_id": int(os.getenv("API_ID_3")), "api_hash": os.getenv("API_HASH_3")},
    {"session": "acc4", "api_id": int(os.getenv("API_ID_4")), "api_hash": os.getenv("API_HASH_4")},
    {"session": "acc5", "api_id": int(os.getenv("API_ID_5")), "api_hash": os.getenv("API_HASH_5")},
]

GROUPS = [
    -1001234567890,
    -1009876543210,
]

MIN_DELAY = 30
MAX_DELAY = 120
