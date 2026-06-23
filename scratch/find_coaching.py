import json
import sys

def find_keys(obj, parent=''):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'coaching' in k:
                found.append(parent + '.' + k)
            found.extend(find_keys(v, parent + '.' + k))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            found.extend(find_keys(item, parent + '[' + str(i) + ']'))
    return found

with open(r'c:\src\quorum\data\files\executions\exe_df88f3323fd441ab8fce2448b01c64a7\execution_trace.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(find_keys(d[3], 'd[3]'))
