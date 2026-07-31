import json

path = r'c:\src\quorum\backend_v2\seed\seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

b = next((b for b in data['prompt_blocks'] if b['id'] == 'blk_22e3598e06414409'), None)
if b:
    print(b)
else:
    print("NOT FOUND")
