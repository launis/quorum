import json

def inspect_details(path):
    print(f"\n=== Details for {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # We check step 6 and 16
    for idx in [6, 16]:
        if idx < len(data):
            step = data[idx]
            content = step.get('content', {})
            print(f"Step {idx}: keys = {list(content.keys())}")
            if '_evaluative_matrices' in content:
                print("  _evaluative_matrices:")
                print(json.dumps(content['_evaluative_matrices'], indent=2, ensure_ascii=False)[:1000])
            if 'scoring_result' in content:
                print("  scoring_result:")
                print(json.dumps(content['scoring_result'], indent=2, ensure_ascii=False)[:1500])
            if 'profiler_metrics' in content:
                print(f"  profiler_metrics: {content['profiler_metrics']}")

inspect_details("data/files/executions/exe_b6c7f868eccf4e8988889daf3ae1dfd4/execution_trace.json")
inspect_details("data/files/executions/exe_2609de8feb6e47db8222e7385c45a796/execution_trace.json")
