import json

trace_path = r'c:\src\quorum\data\files\executions\exe_a09e4fc561db4b64b38b9d66b8e14a7f\execution_trace.json'

with open(trace_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    step_name = item.get('step_name')
    event_type = item.get('event_type')
    
    if event_type == 'input' and 'content' in item:
        print(f"Step: {step_name} | Input keys: {list(item['content'].keys())}")
        if 'inputs' in item['content']:
            print(f"  inputs keys: {list(item['content']['inputs'].keys())}")
    
    if event_type == 'output' and 'content' in item and 'evaluations' in item['content']:
        evals = item['content']['evaluations']
        levels = {}
        for e in evals:
            # We don't have level directly in step_5_boolean? Wait, maybe it's not stored.
            pass
        
        trues = sum(1 for e in evals if e.get('step_5_boolean') is True)
        falses = sum(1 for e in evals if e.get('step_5_boolean') is False)
        print(f"Step: {step_name} | Output Evals: {len(evals)} (True: {trues}, False: {falses})")

