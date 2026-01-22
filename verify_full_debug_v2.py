import json
import os

OUTPUT_FILE = 'c:/src/quorum/verification_full_debug_v2.txt'

def check_sync(out):
    seed_path = 'c:/src/quorum/backend/seed/seed_data.json'
    out.write(f"Checking {seed_path}...\n")
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        out.write(f"Error loading seed: {e}\n")
        return

    # Check Components
    components = data.get('components', [])
    out.write(f"Components Count: {len(components)}\n")
    if len(components) > 0:
        first = components[0]
        out.write(f"  Item[0] Type: {type(first)}\n")
        out.write(f"  Item[0] content: {str(first)[:100]}\n")

    # Check System Config
    sys_conf = data.get('system_config', [])
    out.write(f"System Config Items: {len(sys_conf)}\n")
    if len(sys_conf) > 0:
        first = sys_conf[0]
        out.write(f"  Item[0] Type: {type(first)}\n")
        out.write(f"  Item[0] content: {str(first)[:100]}\n")

def main():
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        check_sync(f)

if __name__ == "__main__":
    main()
