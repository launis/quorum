import json
import sys

trace_path = r'c:\src\quorum\data\files\executions\exe_1e679ec75af04f56b2eaddd7ae4f6d53\execution_trace.json'
with open(trace_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in reversed(data):
    # we just serialize the whole item and look for blk_22e3598e06414409
    item_str = json.dumps(item)
    if 'blk_22e3598e06414409' in item_str or 'blk_c1cc56f65f6a47e1' in item_str:
        print(f"FOUND BLOCK ID IN EVENT TYPE: {item.get('event_type')} (Step: {item.get('step_name')})")
        # Let's extract the part that has this string
        c = item.get('content', {})
        if isinstance(c, dict):
            # check results
            if 'results' in c and isinstance(c['results'], list):
                for res in c['results']:
                    if isinstance(res, dict) and 'matrix_scores' in res:
                        if 'blk_22e3598e06414409' in res['matrix_scores']:
                            print(json.dumps(res['matrix_scores']['blk_22e3598e06414409'], indent=2, ensure_ascii=False))
                            sys.exit(0)
                        if 'blk_c1cc56f65f6a47e1' in res['matrix_scores']:
                            print(json.dumps(res['matrix_scores']['blk_c1cc56f65f6a47e1'], indent=2, ensure_ascii=False))
                            sys.exit(0)
