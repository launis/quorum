import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def find_string(obj, target, path="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_string(v, target, f"{path}.{k}")
            if isinstance(k, str) and target in k:
                print(f"Found {target} in dictionary key at {path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            find_string(v, target, f"{path}[{i}]")
    elif isinstance(obj, str):
        if target in obj:
            print(f"Found {target} in string at {path}")

find_string(data, "prf_e99f728368684813")
find_string(data, "e99f728368684813")
