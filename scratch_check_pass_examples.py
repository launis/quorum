import json

path = r'C:\src\quorum\data\files\executions\exe_ec05ce44941c4d82b4c61dcc84788bb6\execution_trace.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

passes = []
for item in data:
    if item.get('event_type') == 'output':
        parsed = item.get('content', {})
        for ev in parsed.get('evaluations', []):
            if ev.get('status') == 'PASS' and ev.get('exact_quote'):
                passes.append(ev)

for i, p in enumerate(passes[:3]):
    print(f"\n--- ESIMERKKI {i+1} ---")
    print(f"Atom ID: {p.get('atom_id')}")
    print(f"Anchors: {p.get('localized_anchors_found')}")
    print(f"Quote: {p.get('exact_quote')}")
    print(f"Reasoning: {p.get('semantic_reasoning')}")
