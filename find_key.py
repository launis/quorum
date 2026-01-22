def search_file(path, needle):
    print(f"Searching for '{needle}' in {path}...")
    found = False
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if needle in line:
                    print(f"Found at line {i+1}: {line.strip()[:100]}...")
                    found = True
    except Exception as e:
        print(f"Error: {e}")
    
    if not found:
        print("Not found.")

if __name__ == "__main__":
    search_file('c:/src/quorum/backend/seed/seed_data.json', 'model_registry')
    search_file('c:/src/quorum/backend/seed/seed_data.json', 'knowledge_base')
