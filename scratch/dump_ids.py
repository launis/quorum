import json
import os

seed_path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
try:
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    ids = []
    for pb in data.get("prompt_blocks", []):
        ids.append(pb.get("id"))
        
    with open(r"c:\src\quorum\scratch\pb_ids.txt", "w", encoding="utf-8") as out:
        out.write("\n".join(ids))
    print(f"Dumped {len(ids)} ids.")
except Exception as e:
    print(f"Error: {e}")
