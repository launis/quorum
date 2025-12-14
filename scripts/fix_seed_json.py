import json
import os

SEED_Path = r"c:/Users/risto/OneDrive/quorum/backend/database/seed_data.json"

def fix_seed():
    with open(SEED_Path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 1. Remove from STANDARD_REPORT_OUTPUT content
    for comp in data.get('components', []):
        if comp['id'] == 'STANDARD_REPORT_OUTPUT':
            if 'test_dynamic_field' in comp.get('content', []):
                comp['content'].remove('test_dynamic_field')
                print("Removed test_dynamic_field from STANDARD_REPORT_OUTPUT")
        
        # 2. Update instruction_reporter content text
        if comp['id'] == 'instruction_reporter':
            content = comp.get('content', '')
            if "8. Kirjaa testiarvo kenttään 'test_dynamic_field'." in content:
                # Replace the specific line and potentially adjust numbering if needed, 
                # but simplest is to just remove that line.
                # The line is likely "8. Kirjaa ...\n"
                new_content = content.replace("8. Kirjaa testiarvo kenttään 'test_dynamic_field'.\n", "")
                if new_content == content:
                     # Try without newline at end
                     new_content = content.replace("8. Kirjaa testiarvo kenttään 'test_dynamic_field'.", "")
                
                comp['content'] = new_content
                print("Updated instruction_reporter content")

    with open(SEED_Path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Saved seed_data.json")

if __name__ == "__main__":
    fix_seed()
