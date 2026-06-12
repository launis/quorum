import json

scores = {
    'blk_f921c7c0989b47e8': 32.29,
    'blk_109dab5b6b3f403a': 20.88,
    'blk_c3bc5f3eb8e74110': 16.86,
    'blk_f6e286f050c94d60': 15.53,
    'blk_ff72c2d79edb4ebf': 12.71,
    'blk_440a5fef9331451b': 9.87,
    'blk_6b8c766185294f7e': 0.66,
    'blk_22e3598e06414409': 0.53,
    'blk_53f32679aa514fcb': 0.33,
    'blk_c5804a9143c34cb1': 0.26,
    'blk_b476f89fb732448c': 0.06,
    'blk_fb15f8dcf23f4865': 0.008,
    'blk_80732a33fe1947ee': 0.0
}

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        data = json.load(f)

    names = {}
    for block in data.get('prompt_blocks', []):
        try:
            # V2 prompt block format
            fi_name = block['label']['translations']['fi']
            names[block['id']] = fi_name
        except:
            pass

    for eval_obj in data.get('evaluations', []):
        try:
            fi_name = eval_obj['name']['translations']['fi']
            names[eval_obj['id']] = fi_name
        except:
            pass

    print("Scores:")
    for k, v in scores.items():
        print(f"{names.get(k, k)}: {v}")

except Exception as e:
    print(f"Error: {e}")
