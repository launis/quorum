import sys

with open(r'c:\src\quorum\backend_v2\services\blueprint.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '# -- GLOBAL XAI EXTENSION AGGREGATION --' in line:
        skip = True
        
    if skip and 'all_blocks = await self.repo.get_all_prompt_blocks()' in line:
        new_lines.append('        # We must pre-fetch blocks early for resolving axis_label\n')
        new_lines.append(line)
        continue
        
    if skip and 'blocks_by_id = {b["id"]: b for b in all_blocks if "id" in b}' in line:
        new_lines.append(line)
        continue

    if skip and 'layouts_list = []' in line:
        skip = False
        
    if not skip:
        new_lines.append(line)

with open(r'c:\src\quorum\backend_v2\services\blueprint.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
