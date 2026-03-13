import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(list(data.keys()))
