import json
import sys

def traverse_and_fix(node, changes):
    if isinstance(node, dict):
        if 'inputs' in node and isinstance(node['inputs'], dict):
            inputs = node['inputs']
            for k, v in list(inputs.items()):
                if isinstance(v, str) and v in ('$history_text', '$product_text', '$reflection_text'):
                    new_v = '$inputs.' + v[1:]
                    node['inputs'][k] = new_v
                    name = node.get('name', node.get('id', 'Unknown'))
                    changes.append(f"Step '{name}': {k}: {v} -> {new_v}")
        for k, v in node.items():
            traverse_and_fix(v, changes)
    elif isinstance(node, list):
        for item in node:
            traverse_and_fix(item, changes)

def main():
    try:
        with open('backend/seed/seed_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        changes = []
        traverse_and_fix(data, changes)

        if changes:
            with open('backend/seed/seed_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
            print(f"Fixed {len(changes)} mappings:")
            for c in changes:
                print(c)
        else:
            print("No faulty mappings found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
