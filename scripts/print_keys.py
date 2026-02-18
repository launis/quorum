
import json
try:
    with open(r"c:\src\quorum\backend\data\db.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print("KEYS:", list(data.keys()))
except Exception as e:
    print(f"Error: {e}")
