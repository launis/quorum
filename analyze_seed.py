import json
from collections import defaultdict

with open('backend/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

components = data.get('components', [])
type_stats = defaultdict(lambda: {"count": 0, "keys": set(), "content_type": set()})

for comp in components:
    c_type = comp.get('type', 'unknown')
    type_stats[c_type]["count"] += 1
    type_stats[c_type]["keys"].update(comp.keys())
    
    content = comp.get('content')
    if content is not None:
        type_stats[c_type]["content_type"].add(type(content).__name__)
    else:
        type_stats[c_type]["content_type"].add("None")

print(json.dumps({k: {"count": v["count"], "keys": list(v["keys"]), "content_types": list(v["content_type"])} for k, v in type_stats.items()}, indent=2))
