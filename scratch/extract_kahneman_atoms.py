import json
import sys

with open(r'c:\src\quorum\data\files\executions\exe_1e679ec75af04f56b2eaddd7ae4f6d53\execution_trace.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def find_evals(obj):
    found = []
    if isinstance(obj, dict):
        if 'atom_id' in obj and ('status' in obj or 'decision' in obj):
            # It's an evaluation object
            found.append(obj)
        for k, v in obj.items():
            found.extend(find_evals(v))
    elif isinstance(obj, list):
        for item in obj:
            found.extend(find_evals(item))
    return found

all_evals = find_evals(data)
for ev in all_evals:
    rule = ev.get('rule_internalization', '').lower()
    sem = ev.get('semantic_reasoning', '').lower()
    
    # Let's match one of the Kahneman atoms from the screenshot
    if 'heuristiikat' in rule or 'hybris' in rule or 'yksipuolinen' in rule or 'ankkurointi' in rule or 'systemaattinen purkaminen' in rule:
        with open(r'c:\src\quorum\scratch\kahneman_atom.json', 'w', encoding='utf-8') as out:
            json.dump(ev, out, indent=2, ensure_ascii=False)
        print(f"FOUND ATOM EVALUATION! ID: {ev.get('atom_id')}")
        sys.exit(0)

print("Not found :(")
