import json

try:
    with open(r'c:\src\quorum\data\files\executions\exe_85c6f320c91a406fb704539b68a4644e\execution_trace.json', encoding='utf-8') as f:
        trace = json.load(f)

    for item in trace:
        step = item.get('step_name', 'N/A')
        ev_type = item.get('event_type', 'N/A')
        content = item.get('content')
        reasoning = item.get('reasoning')
        meta = item.get('metadata', {})
        score = meta.get('score', 'N/A')
        normalized_score = meta.get('normalized_score', 'N/A')

        print(f"Step: {step} | Type: {ev_type}")
        if score != 'N/A' or normalized_score != 'N/A':
            print(f"  Score: {score} | Normalized: {normalized_score}")

        if isinstance(content, dict):
            if 'exact_quote' in content:
                print(f"  Quote: {content['exact_quote'][:50]}...")
            if 'score' in content:
                print(f"  Content Score: {content['score']}")
            if 'anti_patterns' in content:
                 print(f"  Anti-Patterns: {content['anti_patterns']}")

        if reasoning:
            print(f"  Reasoning: {reasoning[:100]}...")
        print("-" * 40)
except Exception as e:
    print(f"Error: {e}")
