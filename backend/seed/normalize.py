import json

with open('backend/seed/seed_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Keys before:", list(data.keys()))

agents = []
components = []
non_normalized_reports = []

# 1. Separate Agents & Clean fields
current_components = data.get('components', [])
for comp in current_components:
    is_agent = comp.get('type') == 'agent'
    
    # Track non-normalized stuff
    if 'metadata' in comp and comp['metadata']:
        non_normalized_reports.append(f"Component '{comp.get('id')}' had non-empty metadata: {comp['metadata']}")
    if 'model_strategy' in comp:
        non_normalized_reports.append(f"Component '{comp.get('id')}' had model_strategy: {comp['model_strategy']}")
    if comp.get('config', {}).get('model_strategy'):
        non_normalized_reports.append(f"Component '{comp.get('id')}' had model_strategy in config")

    # Clean
    for key in ['hoist_keys', 'metadata', 'model_strategy']:
        comp.pop(key, None)
        if 'config' in comp and isinstance(comp['config'], dict):
            comp['config'].pop(key, None)

    if is_agent:
        comp.pop('type', None) # Removing type since it is in agents table now
        agents.append(comp)
    else:
        components.append(comp)

data['agents'] = agents
data['components'] = components

# 2. Check Workflows for non-normalized data
for w in data.get('workflows', []):
    if 'metadata' in w or 'config' in w:
        non_normalized_reports.append(f"Workflow '{w.get('id')}' has unwanted metadata or config")
        w.pop('metadata', None)
        w.pop('config', None)

# 3. Check steps for non-normalized data
for s in data.get('steps', []):
    if 'metadata' in s or 'hoist_keys' in s or 'model_strategy' in s:
        non_normalized_reports.append(f"Step '{s.get('id')}' has unwanted metadata, hoist_keys, or model_strategy")
        s.pop('metadata', None)
        s.pop('hoist_keys', None)
        s.pop('model_strategy', None)
        if 'config' in s and isinstance(s['config'], dict):
            s['config'].pop('model_strategy', None)
            s['config'].pop('hoist_keys', None)

with open('backend/seed/seed_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Keys after:", list(data.keys()))
print("----- NON-NORMALIZED DATA REPORT -----")
for r in non_normalized_reports:
    print(r)
print("--------------------------------------")
