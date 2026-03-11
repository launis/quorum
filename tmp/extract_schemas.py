import json
import re
from pathlib import Path

seed_path = Path('c:/src/quorum/backend_v2/seed/seed_data.json')
with open(seed_path, encoding='utf-8') as f:
    data = json.load(f)

blocks = data.get('prompt_blocks', [])

schema_pattern = re.compile(r'\(([\w]+)\)[^\w]*\{\{SCHEMA_EXAMPLE\}\}')

print("--- Schemas required by blocks ---")
found_schemas = set()

for pb in blocks:
    desc = pb.get('description', {}).get('translations', {}).get('fi', '')
    match = schema_pattern.search(desc)
    if match:
        schema_name = match.group(1)
        found_schemas.add(schema_name)
        print(f"{pb['id']}: {schema_name}")
    elif '{{SCHEMA_EXAMPLE}}' in desc:
        print(f"[{pb['id']}] WARNING: Has SCHEMA_EXAMPLE but could not parse name!")
        # Print surrounding context
        idx = desc.find('{{SCHEMA_EXAMPLE}}')
        print("   " + desc[max(0, idx-50):idx+50])

print("\n--- Summary of Required Schemas ---")
for s in sorted(found_schemas):
    print("- " + s)
