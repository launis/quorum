import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))
for sp in d.get("steps", []):
    name = sp.get("name", {}).get("translations", {}).get("fi", "").lower()
    if any(t in name for t in ["falsifier", "logician", "overseer", "judge", "analyst"]):
        print(f"Name: {name}, ID: {sp.get('id')}, Strategy: {sp.get('model_strategy')}")
