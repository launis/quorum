import json
import shutil
import os
import copy

def update_titles():
    seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
    bak_path = 'c:/src/quorum/backend_v2/seed/seed_data.json.title_bak'
    
    shutil.copy2(seed_path, bak_path)
    print(f"Backed up {seed_path} to {bak_path}")

    with open(seed_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    blocks = {b['id']: b for b in data.get('prompt_blocks', [])}

    for prof in data.get('output_profiles', []):
        for i, layout in enumerate(prof.get('layouts', [])):
            if layout.get('preset_view') in ['1d_metrics', '2d_compare', '3d_matrix', '3d_complex']:
                targets = layout.get('target_blocks', [])
                if not targets:
                    continue

                if layout.get('preset_view') == '1d_metrics':
                    # Extract from the target block
                    if len(targets) != 1:
                        print(f"Warning: 1D matrix layout {i} has {len(targets)} targets.")
                    
                    b = blocks.get(targets[0])
                    if not b:
                        print(f"Warning: Block {targets[0]} not found.")
                        continue
                    
                    title = None
                    if b.get('rows') and len(b['rows']) > 0:
                        title = copy.deepcopy(b['rows'][0].get('label'))
                    
                    desc = copy.deepcopy(b.get('description'))
                    if desc and 'default_locale' not in desc:
                         if isinstance(desc, str):
                              desc = {'default_locale': 'fi', 'translations': {'fi': desc, 'en': desc}}

                    # Update layout
                    if title:
                        layout['title'] = title
                    if desc:
                        layout['description'] = desc

                else:
                    # For 2D / 3D, just ensure they have non-null title and description with translations
                    title = layout.get('title')
                    desc = layout.get('description')
                    
                    if not title or 'translations' not in title:
                        print(f"Warning: Layout {i} ({layout.get('preset_view')}) lacks proper title.")
                    elif not title['translations'].get('fi') or not title['translations'].get('en'):
                         print(f"Warning: Layout {i} ({layout.get('preset_view')}) title lacks fi or en.")
                         
                    if not desc or 'translations' not in desc:
                        print(f"Warning: Layout {i} ({layout.get('preset_view')}) lacks proper description.")
                    elif not desc['translations'].get('fi') or not desc['translations'].get('en'):
                         print(f"Warning: Layout {i} ({layout.get('preset_view')}) desc lacks fi or en.")

    with open(seed_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
    print("Updated seed_data.json.")

if __name__ == '__main__':
    update_titles()
