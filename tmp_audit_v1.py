import json

def analyze_v1_components():
    with open('c:/src/quorum/data/github_seed_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data.get('components', [])
    if isinstance(components, dict):
        components = list(components.values())
        
    candidates = []
    
    for comp in components:
        name = comp.get('name') or comp.get('slug', 'Unnamed')
        v1_type = comp.get('type', '')
        scales = comp.get('scales', [])
        content = comp.get('content') or comp.get('explanation', '')
        
        # We are looking for things that DO NOT have scales
        if not scales and v1_type != 'instruction':
            candidates.append({
                'name': name,
                'content': content[:150].replace('\n', ' ')
            })
            
    with open('c:/src/quorum/tmp_v1_candidates.txt', 'w', encoding='utf-8') as out:
        out.write(f"Found {len(candidates)} components without scales (excluding 'instruction' types).\n\n")
        for idx, c in enumerate(candidates):
            out.write(f"{idx+1}. {c['name']} -> {c['content']}\n")

if __name__ == '__main__':
    analyze_v1_components()
