import json

try:
    with open(r'c:\src\quorum\data\files\executions\exe_4f218b3e222347a69a41e46b2fdf7079\execution_trace.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ensemble_found = False
    for event in data:
        meta = event.get('metadata', {})
        if 'is_ensemble_step' in meta:
            print(f"Event {event['event_type']} in {event['step_name']} has is_ensemble_step = {meta['is_ensemble_step']}")
            ensemble_found = True
            
        content = event.get('content', {})
        if isinstance(content, dict):
            for k, v in content.items():
                if k.startswith("tda_") and isinstance(v, list) and len(v) > 1:
                    print(f"Found {len(v)} evaluations for {k} in {event['step_name']} (Ensemble detected!)")
                    ensemble_found = True
                    break
    if not ensemble_found:
        print("No ensemble executions detected. All evaluations appear to be Zero-Shot (length 1 or dict).")
except Exception as e:
    print("Error:", e)
