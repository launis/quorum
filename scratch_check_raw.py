import json

path = r'C:\src\quorum\data\files\executions\exe_ec05ce44941c4d82b4c61dcc84788bb6\execution_trace.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item.get('event_type') == 'output':
        step_name = item.get('step_name')
        raw_res = item.get('content', {}).get('raw_response', '')
        if raw_res:
            print(f"\nRAW RESPONSE FOR {step_name}:")
            print(raw_res[:500])
        else:
            print(f"\nRAW RESPONSE FOR {step_name} IS EMPTY/NULL")
