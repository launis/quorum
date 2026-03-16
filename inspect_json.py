import json
import sys

def find_tokens(data, path=''):
    if isinstance(data, dict):
        if 'token' in path.lower() or any('token' in k.lower() for k in data.keys()):
            subset = {k: v for k, v in data.items() if 'token' in k.lower()}
            if subset: print(f"Found at {path}: {subset}")
        for k, v in data.items():
            find_tokens(v, f"{path}.{k}" if path else k)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            find_tokens(item, f"{path}[{i}]")

try:
    with open('C:/Users/risto/Downloads/debug_output_20260316_141941.json', encoding='utf-8') as f:
        data = json.load(f)
        find_tokens(data)
except Exception as e:
    print(f"Error: {e}")
