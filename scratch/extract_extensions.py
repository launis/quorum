import json

with open("backend_v2/seed/seed_data.json", encoding="utf-8") as f:
    data = json.load(f)

def extract_values_for_keys(obj, target_keys, results=set()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in target_keys:
                if isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            results.add(item)
                elif isinstance(v, str):
                    results.add(v)
            extract_values_for_keys(v, target_keys, results)
    elif isinstance(obj, list):
        for i in obj:
            extract_values_for_keys(i, target_keys, results)
    return results

target = {'visible_workflow_extensions', 'visible_block_extensions', 'output_extensions'}
print("Extension strings:", extract_values_for_keys(data, target))

# For extension_labels, we want the keys of the dict
def extract_keys_from_dict_keys(obj, target_keys, results=set()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in target_keys and isinstance(v, dict):
                for sub_k in v.keys():
                    results.add(sub_k)
            extract_keys_from_dict_keys(v, target_keys, results)
    elif isinstance(obj, list):
        for i in obj:
            extract_keys_from_dict_keys(i, target_keys, results)
    return results

print("Extension labels keys:", extract_keys_from_dict_keys(data, {'extension_labels'}))
