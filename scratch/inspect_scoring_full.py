import json

def inspect_matrices_anywhere(path):
    print(f"\n=== Searching for matrices in {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Let's inspect step 16 content more closely
    step_16 = data[16]
    content = step_16.get('content', {})
    
    # We look for any keys in content['steps'] or content['inputs'] or scoring_result
    print(f"Keys in content: {list(content.keys())}")
    
    # If there is scoring_result, let's dump its entire dict
    scoring_result = content.get('scoring_result', {})
    print("scoring_result full keys:", list(scoring_result.keys()))
    print("scoring_result content:")
    print(json.dumps(scoring_result, indent=2, ensure_ascii=False))

inspect_matrices_anywhere("data/files/executions/exe_b6c7f868eccf4e8988889daf3ae1dfd4/execution_trace.json")
inspect_matrices_anywhere("data/files/executions/exe_2609de8feb6e47db8222e7385c45a796/execution_trace.json")
