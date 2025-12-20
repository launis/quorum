import json

def compare():
    try:
        # Load OLD
        with open('scripts/old_seed.json', 'r', encoding='utf-8') as f:
            old_data = json.load(f)
            
        # Load NEW
        with open('backend/database/seed_data.json', 'r', encoding='utf-8') as f:
            new_data = json.load(f)
            
        def get_content(data, cid):
            for c in data.get('components', []):
                if c['id'] == cid:
                    return c['content']
            return "NOT FOUND"

        print("--- TASK_GUARD ---")
        print("OLD:", get_content(old_data, 'TASK_GUARD')[:200] + "...")
        print("NEW:", get_content(new_data, 'TASK_GUARD')[:200] + "...")
        
        print("\n--- TASK_JUDGE ---")
        print("OLD:", get_content(old_data, 'TASK_JUDGE')[:200] + "...")
        print("NEW:", get_content(new_data, 'TASK_JUDGE')[:200] + "...")
        
        print("\n--- GLOBAL_CONTEXT ---")
        print("OLD:", get_content(old_data, 'GLOBAL_CONTEXT')[:100] + "...")
        print("NEW:", get_content(new_data, 'GLOBAL_CONTEXT')[:200] + "...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    compare()
