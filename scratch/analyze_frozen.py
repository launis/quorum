import json

try:
    with open(r'c:\src\quorum\data\files\executions\exe_85c6f320c91a406fb704539b68a4644e\frozen_context.json', encoding='utf-8') as f:
        data = json.load(f)

    print("Keys in frozen_context:", data.keys())

    # If there's a metrics or score object
    if 'metrics' in data:
        print("\n--- Metrics ---")
        for k, v in data['metrics'].items():
            if not isinstance(v, dict) and not isinstance(v, list):
                print(f"{k}: {v}")

    # Let's see if we have steps or observations
    if 'observations' in data:
        obs = data['observations']
        print(f"\n--- Observations ({len(obs)}) ---")
        for k, v in obs.items():
            val = v.get('value', {})
            score = val.get('score', 'N/A')
            ap = val.get('anti_patterns', [])
            exact = val.get('exact_quote', '')
            print(f"Obs: {k} | Score: {score} | Anti-patterns: {len(ap)} | Exact quote len: {len(exact)}")

    # Or in 'workflow_state'
    if 'workflow_state' in data:
        print("\n--- Workflow State keys ---")
        print(data['workflow_state'].keys())

except Exception as e:
    print(f"Error: {e}")
