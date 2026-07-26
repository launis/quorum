import json

def find_text(data, path=""):
    if isinstance(data, dict):
        for k, v in data.items():
            find_text(v, f"{path}.{k}")
    elif isinstance(data, list):
        for i, v in enumerate(data):
            find_text(v, f"{path}[{i}]")
    elif isinstance(data, str):
        lowered = data.lower()
        if "rooli" in lowered or "role" in lowered:
            print(f"FOUND AT: {path}")
            print(f"CONTENT: {data[:200]}...")

with open("c:/src/quorum/old_seed.json", encoding="utf-16") as f:
    data = json.load(f)
find_text(data)
