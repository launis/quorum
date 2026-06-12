import json
import os

folder = r'C:\src\quorum\data\files\executions\exe_a2f8229bcb264fbe885c48b9aca22f3e'
state_path = os.path.join(folder, 'state.json')
trace_path = os.path.join(folder, 'execution_trace.json')

if os.path.exists(state_path):
    with open(state_path, encoding='utf-8') as f:
        state = json.load(f)

    print('--- STATE JSON ---')
    print(f"Final Score: {state.get('final_score')}")
    print(f"Penalties: {state.get('penalties')}")

    matrices = {}
    gcv = state.get('global_context_vars', {})
    if gcv:
        steps = gcv.get('steps', [])
        for step in steps:
            if step.get('block_id') == '_evaluative_matrices':
                matrices = step.get('payload', {})
                break

    if matrices:
        print('\n--- MATRICES ---')
        for k, v in matrices.items():
            print(f'{k}: {v}')

if os.path.exists(trace_path):
    with open(trace_path, encoding='utf-8') as f:
        trace = json.load(f)

    pass_count = 0
    fail_count = 0
    sys_count = 0
    for item in trace:
        if item.get('event_type') == 'output':
            parsed = item.get('content', {})
            for ev in parsed.get('evaluations', []):
                status = ev.get('status', '')
                reason = ev.get('semantic_reasoning', '')
                if 'LLM Unable to verify' in reason or 'SYSTEM ERROR' in reason:
                    sys_count += 1
                elif status == 'PASS':
                    pass_count += 1
                else:
                    fail_count += 1

    print('\n--- TRACE SUMMARY ---')
    print(f'Pass: {pass_count}, Fail: {fail_count}, System Error: {sys_count}')
