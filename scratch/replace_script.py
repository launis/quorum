import json

seed_file = r'c:\src\quorum\backend_v2\seed\seed_data.json'
with open(seed_file, encoding='utf-8') as f:
    d = json.load(f)

old_text = d['output_profiles'][0]['synthesis']['system_prompt']
new_text = old_text.replace(
    'using EXACTLY the raw enum value from the data (e.g., "**Käyttäjän Rooli: ROLE_ARCHITECT**"). DO NOT translate the enum value (ROLE_ARCHITECT, ROLE_DRIVER, ROLE_NAVIGATOR, ROLE_PASSENGER).',
    'using the translated role value from the data (e.g., "**Käyttäjän Rooli: Arkkitehti**" or "**User Role: Architect**"). Do not invent a role; use the exact localized role name provided in the execution context.'
)

# Handle the case where unicode \u00e4 is used
new_text = new_text.replace(
    'using EXACTLY the raw enum value from the data (e.g., "**K\u00e4ytt\u00e4j\u00e4n Rooli: ROLE_ARCHITECT**"). DO NOT translate the enum value (ROLE_ARCHITECT, ROLE_DRIVER, ROLE_NAVIGATOR, ROLE_PASSENGER).',
    'using the translated role value from the data (e.g., "**K\u00e4ytt\u00e4j\u00e4n Rooli: Arkkitehti**" or "**User Role: Architect**"). Do not invent a role; use the exact localized role name provided in the execution context.'
)

if old_text != new_text:
    d['output_profiles'][0]['synthesis']['system_prompt'] = new_text
    with open(seed_file, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
    print('SUCCESS')
else:
    print('NO CHANGES MADE')
