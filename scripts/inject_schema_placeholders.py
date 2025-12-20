import json

SEED_FILE = "backend/database/seed_data.json"

def inject_placeholders():
    try:
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        components = data.get('components', [])
        updated_count = 0
        
        for comp in components:
            if comp['id'].startswith("TASK_"):
                content = comp.get('content', '')
                if "{{SCHEMA_EXAMPLE}}" not in content:
                    # Append strict JSON instruction
                    new_content = content + "\n\nKÄSKE: Tulosta vastauksesi TÄSMÄLLEEN seuraavan JSON-skeeman mukaisesti (älä muuta kenttien nimiä):\n{{SCHEMA_EXAMPLE}}"
                    comp['content'] = new_content
                    updated_count += 1
                    print(f"Updated {comp['id']}")
                    
        data['components'] = components
        
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Injection complete. Updated {updated_count} tasks.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inject_placeholders()
