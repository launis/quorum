import json
import os

trace_path = r'c:\src\quorum\data\files\executions\exe_a09e4fc561db4b64b38b9d66b8e14a7f\execution_trace.json'

with open(trace_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    step_name = item.get('step_name')
    event_type = item.get('event_type')
    
    if event_type == 'output' and 'content' in item and 'evaluations' in item['content']:
        evals = item['content']['evaluations']
        trues = sum(1 for e in evals if e.get('step_5_boolean') is True)
        falses = sum(1 for e in evals if e.get('step_5_boolean') is False)
        print(f"Step: {step_name} | Evals: {len(evals)} (True: {trues}, False: {falses})")
    elif event_type == 'output':
        print(f"Step: {step_name} | Output, no evals.")
    else:
        print(f"Step: {step_name} | {event_type}")

