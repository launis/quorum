import json

path = r'C:\src\quorum\data\files\executions\exe_ec05ce44941c4d82b4c61dcc84788bb6\execution_trace.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    s = json.dumps(item)
    if 'LLM Unable to verify' in s:
        print(f"Found in step: {item.get('step_name')}")
