import json

trace_path = r'c:\src\quorum\data\files\executions\exe_add8965fdc7342c5950678fd9745dfb6\execution_trace.json'
with open(trace_path, encoding='utf-8') as f:
    trace = json.load(f)

for step in trace:
    print(f"Step ID: {step.get('step_id')}")
    out = step.get('outputs', {})
    if isinstance(out, dict):
        print(f"  Outputs keys: {list(out.keys())}")
        if 'atoms' in out:
            print(f"  atoms list size: {len(out['atoms'])}")
            if len(out['atoms']) > 0:
                print(f"  first atom keys: {list(out['atoms'][0].keys())}")
        elif 'evaluations' in out:
            print(f"  evaluations list size: {len(out['evaluations'])}")
