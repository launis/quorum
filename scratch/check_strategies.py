import json

d = json.load(open(r"c:\src\quorum\backend_v2\seed\seed_data.json", "r", encoding="utf-8"))

def find_keys(obj, target):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and target.lower() in v.lower():
                print(f"Found '{target}' in dict key '{k}': {v[:50]}...")
            find_keys(v, target)
    elif isinstance(obj, list):
        for item in obj:
            find_keys(item, target)

print("Searching for Analyst...")
find_keys(d.get("workflows", []), "Analyst")
