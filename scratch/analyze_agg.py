import json
from collections import defaultdict

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

stats = defaultdict(list)

def extract_tdas(obj):
    if isinstance(obj, dict):
        if "tda_assertions" in obj and isinstance(obj["tda_assertions"], list):
            for tda in obj["tda_assertions"]:
                agg = tda.get("aggregation_mode")
                inv = tda.get("inverse_evidence")
                key = f"Agg: {agg}, Inv: {inv}"
                stats[key].append(tda.get("ai_rule_description", "")[:100].replace('\n', ' '))
        for k, v in obj.items():
            extract_tdas(v)
    elif isinstance(obj, list):
        for item in obj:
            extract_tdas(item)

extract_tdas(data)

for key, items in stats.items():
    print(f"\n{key} -> COUNT: {len(items)}")
    print("Samples:")
    for item in items[:5]:
        print(f"  - {item}...")
