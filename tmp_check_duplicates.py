import json

with open(r'c:\src\quorum\backend_v2\seed\seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

blocks = data['prompt_blocks']
b = next((b for b in blocks if b['id'] == 'blk_22e3598e06414409'), None)
print(b['slug'] if b else "NOT FOUND")
