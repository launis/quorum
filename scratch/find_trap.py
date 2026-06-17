import json

path1 = r'c:\src\quorum\data\files\executions\exe_59b39925936544eebf9e474a02eec1fa\execution_trace.json'
with open(path1, encoding='utf-8') as f:
    data = json.load(f)

for x in data:
    if x.get('event_type') == 'output' and 'content' in x and 'reasoning_trace' in x['content']:
        trace = x['content']['reasoning_trace']
        if 'virheetön' in trace.lower() or 'kyseenalaista' in trace.lower():
            print("\n=== LÖYDETTY ANSALAUSEEN KÄSITTELY ===")
            print(f"Step: {x.get('step_name')}")
            print(f"Notes: {x['content'].get('evaluation_notes')}")
            print(f"Trace:\n{trace}")
