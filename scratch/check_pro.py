import json

with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    data = json.load(f)

strategies = {}
for table_name, table_data in data.items():
    if table_name == 'SystemConfig':
        for k, v in table_data.items():
            if v.get('id') == 'model_registry':
                strategies = v.get('models', {})

pro_strategies = {}
for name, config in strategies.items():
    model = config.get('model_name', '')
    if 'pro' in model:
        pro_strategies[name] = config

for name, config in pro_strategies.items():
    print(f'Strategy: {name}')
    print(f"  Model: {config.get('model_name')}")
    print(f"  Max Tokens: {config.get('max_tokens')}")
    print(f"  Caching: {config.get('caching_strategy')}")
    print('---')
