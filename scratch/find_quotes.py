import json
import sys

trace_path = r'c:\src\quorum\data\files\executions\exe_1e679ec75af04f56b2eaddd7ae4f6d53\execution_trace.json'
with open(trace_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in reversed(data):
    c = item.get('content', {})
    if not isinstance(c, dict): continue
    
    # Sometimes it's inside 'scoring_result' -> 'matrix_scores'
    if 'scoring_result' in c:
        sr = c['scoring_result']
        if 'matrix_scores' in sr and 'blk_109dab5b6b3f403a' in sr['matrix_scores']:
            with open(r'c:\src\quorum\scratch\matrix_score.json', 'w', encoding='utf-8') as out:
                json.dump(sr['matrix_scores']['blk_109dab5b6b3f403a'], out, indent=2, ensure_ascii=False)
            print("FOUND IN SCORING_RESULT!")
            sys.exit(0)
    
    # Or 'state' -> 'scoring_result'
    if 'state' in c and isinstance(c['state'], dict):
        if 'scoring_result' in c['state'] and 'matrix_scores' in c['state']['scoring_result']:
            if 'blk_109dab5b6b3f403a' in c['state']['scoring_result']['matrix_scores']:
                with open(r'c:\src\quorum\scratch\matrix_score.json', 'w', encoding='utf-8') as out:
                    json.dump(c['state']['scoring_result']['matrix_scores']['blk_109dab5b6b3f403a'], out, indent=2, ensure_ascii=False)
                print("FOUND IN STATE SCORING_RESULT!")
                sys.exit(0)

# If we haven't found it in the structured way, let's just do a recursive search
def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for k, v in obj.items():
            res = find_key(v, key)
            if res is not None:
                return res
    elif isinstance(obj, list):
        for item in obj:
            res = find_key(item, key)
            if res is not None:
                return res
    return None

for item in reversed(data):
    res = find_key(item, 'blk_109dab5b6b3f403a')
    if res is not None:
        with open(r'c:\src\quorum\scratch\matrix_score.json', 'w', encoding='utf-8') as out:
            json.dump(res, out, indent=2, ensure_ascii=False)
        print("FOUND VIA RECURSIVE SEARCH!")
        sys.exit(0)

