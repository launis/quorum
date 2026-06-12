import json

path = r'C:\src\quorum\data\files\executions\exe_ec05ce44941c4d82b4c61dcc84788bb6\frozen_context.json'
with open(path, encoding='utf-8') as f:
    data = json.load(f)

prompts = data.get('compiled_prompts', {})
for k, v in prompts.items():
    print(f"\n=================== STEP {k} PROMPT ===================")
    print(v.get('user_payload')[:2000]) # First 2000 chars of user payload
    break
