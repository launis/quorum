import json

seed_path = r'c:\src\quorum\backend_v2\seed\seed_data.json'

with open(seed_path, encoding='utf-8') as f:
    data = json.load(f)

workflows = data.get('workflows', [])
count = 0

for wf in workflows:
    if 'scoring_logic' in wf:
        del wf['scoring_logic']
        count += 1

with open(seed_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Removed scoring_logic from {count} workflows.")
