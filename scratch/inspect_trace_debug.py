import json

def inspect(path):
    print(f"\n=== Inspecting {path} ===")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total steps: {len(data)}")
    
    # We want to find:
    # 1. Any step containing matrices or scores
    # 2. Any step containing control_ratio or behavioral_metrics
    # 3. Any step containing synthesis or highlights
    for i, step in enumerate(data):
        step_id = step.get('step_id', '')
        step_type = step.get('step_type', '')
        content = step.get('content', {})
        
        # Look for matrices or scoring
        if 'matrix' in step_id or 'matrix' in step_type or 'scoring' in step_type:
            print(f"Matrix step: index={i}, id={step_id}, type={step_type}")
            if isinstance(content, dict):
                print(f"  keys: {list(content.keys())}")
                if 'evaluative_matrices' in content:
                    print(f"    evaluative_matrices keys: {list(content['evaluative_matrices'].keys()) if isinstance(content['evaluative_matrices'], dict) else 'not dict'}")
                if 'matrices' in content:
                    print(f"    matrices count: {len(content['matrices'])}")
                    for m in content['matrices']:
                        print(f"      Matrix: {m.get('id')} / {m.get('name')} -> score: {m.get('score')} or {m.get('normalized_score')}")
                if 'normalized_score' in content:
                    print(f"    normalized_score: {content['normalized_score']}")
                if 'score' in content:
                    print(f"    score: {content['score']}")

        # Look for control_ratio or role
        if isinstance(content, dict):
            content_str = str(content)
            if 'control_ratio' in content_str or 'behavioral_metrics' in content_str:
                print(f"Control ratio step: index={i}, id={step_id}, type={step_type}")
                # print some keys or subset of content
                for k, v in content.items():
                    if 'control_ratio' in str(k) or 'control_ratio' in str(v) or 'metrics' in str(k):
                        print(f"  {k}: {str(v)[:200]}")
            
            if 'role' in content_str and ('architect' in content_str.lower() or 'driver' in content_str.lower() or 'navigator' in content_str.lower()):
                print(f"Role/Synthesis step: index={i}, id={step_id}, type={step_type}")
                print(f"  keys: {list(content.keys())}")
                # check if there is an executive summary or synthesis
                if 'synthesis' in content:
                    print(f"    synthesis snippet: {str(content['synthesis'])[:300]}")
                if 'profile_synthesis' in content:
                    print(f"    profile_synthesis keys: {list(content['profile_synthesis'].keys()) if isinstance(content['profile_synthesis'], dict) else 'not dict'}")
                if 'summary' in content:
                    print(f"    summary snippet: {str(content['summary'])[:300]}")

inspect("data/files/executions/exe_b6c7f868eccf4e8988889daf3ae1dfd4/execution_trace.json")
inspect("data/files/executions/exe_2609de8feb6e47db8222e7385c45a796/execution_trace.json")
