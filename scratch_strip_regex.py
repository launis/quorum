import re

with open(r'c:\src\quorum\backend_v2\services\blueprint.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Specifically purge bad dictionary fallbacks: get('key', []) and get('key', {}) and get('key', '')
content = re.sub(r'\.get\(([\"\'][a-zA-Z0-9_\-]+[\"\']),\s*\[\]\)', r'.get(\1)', content)
content = re.sub(r'\.get\(([\"\'][a-zA-Z0-9_\-]+[\"\']),\s*\{\}\)', r'.get(\1)', content)
content = re.sub(r'\.get\(([\"\'][a-zA-Z0-9_\-]+[\"\']),\s*[\"\'][\"\']\)', r'.get(\1)', content)

# Purge 0 float and int defaults in get
content = re.sub(r'\.get\(([\"\'][a-zA-Z0-9_\-]+[\"\']),\s*0\)', r'.get(\1)', content)
content = re.sub(r'\.get\(([\"\'][a-zA-Z0-9_\-]+[\"\']),\s*0\.0\)', r'.get(\1)', content)

# Print any remaining gets with commas
lines = content.split('\n')
for i, line in enumerate(lines):
    if '.get(' in line and ',' in line:
        print(f"Remaining get with comma at line {i+1}: {line.strip()}")

with open(r'c:\src\quorum\backend_v2\services\blueprint.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
