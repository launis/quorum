import json

path = 'backend_v2/seed/seed_data.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for wf in data.get('workflows', []):
    old_mapping = wf.pop('output_mapping', {})
    preset_view = old_mapping.get('preset_view', '1d_metrics')
    
    wf['output_profiles'] = {
        'default': {
            'name': {'fi': 'Oletusprofiili', 'en': 'Default Profile'},
            'layouts': [
                {
                    'preset_view': preset_view,
                    'steps': [],
                    'show_text': True
                }
            ]
        }
    }

with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print('Migration successful')
