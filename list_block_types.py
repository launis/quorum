import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

prefixes = {}
for block in data.get("prompt_blocks", []):
    id_str = block["id"]
    prefix = id_str.split("_")[0]
    if prefix == "block":
        parts = id_str.split("_")
        if len(parts) > 1:
             prefix = f"block_{parts[1]}"
             
    if prefix not in prefixes:
         prefixes[prefix] = []
    prefixes[prefix].append(id_str)

for p, items in prefixes.items():
    print(f"\n--- {p.upper()} ---")
    for item in items:
        print(f"  {item}")
