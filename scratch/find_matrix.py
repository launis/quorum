import json

with open(r'c:\src\quorum\data\files\executions\exe_1e679ec75af04f56b2eaddd7ae4f6d53\frozen_context.json', 'r', encoding='utf-8') as f:
    fc = json.load(f)

for k, v in fc.get('ui_hints_snapshot', {}).items():
    if 'kahneman' in str(v).lower() or 'harkintakyky' in str(v).lower():
        print(f"Matrix ID: {k}")
        print(f"Matrix definition: {json.dumps(v, indent=2, ensure_ascii=False)}")

