import json

path = 'backend_v2/seed/seed_data.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

target_extensions = [
    "justification",
    "falsification",
    "coaching",
    "remediation_steps"
]

full_extensions = [
    "citation",
    "justification",
    "falsification",
    "theory_link",
    "risk_flag",
    "coaching",
    "missing_context",
    "remediation_steps",
    "emotional_sentiment",
    "confidence",
    "source_id"
]

replaced_count = 0

def process_item(item):
    global replaced_count
    if isinstance(item, dict):
        # Check if output_extensions is present and matches the target exactly
        if "output_extensions" in item and isinstance(item["output_extensions"], list):
            if item["output_extensions"] == target_extensions:
                item["output_extensions"] = full_extensions
                replaced_count += 1
        
        # Recurse into all dictionary values
        for v in item.values():
            process_item(v)
            
    elif isinstance(item, list):
        for v in item:
            process_item(v)

process_item(data)

if replaced_count > 0:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Success! Replaced {replaced_count} occurrences of output_extensions.")
else:
    print("No matches found.")
