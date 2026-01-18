
import json

def extract_prompt():
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data.get('components', [])
    for c in components:
        if c.get('id') == 'TASK_ANALYST':
            with open('temp_analyst_prompt.txt', 'w', encoding='utf-8') as out:
                out.write(c.get('content', ''))
            print("Prompt saved to temp_analyst_prompt.txt")
            return

if __name__ == "__main__":
    extract_prompt()
