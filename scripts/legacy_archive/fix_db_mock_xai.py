import json
import os


files_to_fix = [
    r'c:\Users\risto\OneDrive\quorum\data\db_mock.json',
    r'c:\Users\risto\OneDrive\quorum\data\seed_data.json'
]

def fix_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    print(f"Processing: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Fix Component 58 (XAIReporterAgent)
    components = data.get('components', {})
    if '58' in components:
        comp = components['58']
        if comp.get('name') == 'XAIReporterAgent':
            print(f"Found XAIReporterAgent. Current module: {comp.get('module')}")
            comp['module'] = 'backend.agents.xai'
            print(f"Updated module to: {comp['module']}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully updated and pretty-printed {file_path}")

if __name__ == "__main__":
    for p in files_to_fix:
        fix_json_file(p)

