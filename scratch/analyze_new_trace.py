import json
from collections import defaultdict

trace_path = r'c:\src\quorum\data\files\executions\exe_90b176274d4e456bae89d3f503f19658\execution_trace.json'

with open(trace_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

scores = []

for item in data:
    if item.get('event_type') == 'output':
        content = item.get('content', {})
        for key, val in content.items():
            if key.startswith('blk_'):
                if isinstance(val, dict):
                    items = [val]
                elif isinstance(val, list):
                    items = val
                else:
                    continue
                    
                for i in items:
                    if not isinstance(i, dict): continue
                    
                    score = i.get('raw_score')
                    if score is not None:
                        scores.append((key, score, i.get('scaled_score')))
                        
for s in scores:
    print(f"Block: {s[0]} | Raw: {s[1]} | Scaled: {s[2]}")
