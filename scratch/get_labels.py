import json

try:
    with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
        seed_data = json.load(f)

    for block in seed_data.get('prompt_blocks', []):
        if block['id'] in ['blk_80732a33fe1947ee', 'blk_22e3598e06414409', 'blk_109dab5b6b3f403a', 'blk_c3bc5f3eb8e74110', 'blk_440a5fef9331451b', 'blk_b476f89fb732448c', 'blk_c5804a9143c34cb1', 'blk_fb15f8dcf23f4865', 'blk_f6e286f050c94d60', 'blk_f921c7c0989b47e8', 'blk_ff72c2d79edb4ebf', 'blk_53f32679aa514fcb', 'blk_6b8c766185294f7e']:
            label = block.get('label', {}).get('fi', block.get('label', {}).get('en', 'N/A'))
            print(f"{block['id']} -> {label}")

except Exception as e:
    print(f"Error: {e}")
